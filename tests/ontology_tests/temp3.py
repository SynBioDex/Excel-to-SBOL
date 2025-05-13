import rdflib
import os
import sbol3
import excel_sbol_utils.helpers as h

direct = os.path.split(__file__)[0]
file_path_in = os.path.join(direct, 'two_backbones.nt')

# Purpose: After converting the combinatorial derivations, the references to the objects in other parts must be updated
# Input: SBOL3 Document object, SBOL3 Dictionary of combinatorial derivations after conversion
# Output: Updated SBOL3 Document object

def updateVariableFeatures(doc, combdev):
    # 1: Loop through every item in the combdev dictionary
    for item in combdev:
        # 2 Cases: Has a backbone and therefore variable features located in insert, or located inside the original object
        convVar = []
        ins = True # If the object has an insert
        edited = False # If the variable features are edited 

        insert = item + "_ins"
        obj = doc.find(insert)

        if obj == None or type(obj) != sbol3.combderiv.CombinatorialDerivation:
            ins = False
            obj = doc.find(item)
            obj.strategy = sbol3.SBOL_ENUMERATE # Check This line

        if doc.find(f'{insert}_template'):
            template = doc.find(f'{insert}_template')
        else:
            template = doc.find(f'{item}_template')


        # 2: Go through every variable feature
        for variable_feature in list(obj.variable_features):

            # Go through and ensure that variantderivations are correct

            removeList = [] # List of variants to remove
            addList = [] # List of variants to add as a subcomponent

            # combdev list of changed from combinatorial derivations to components
            for variant in variable_feature.variants:
                if str(variant) in combdev:
                    addList.append(variant)
                    removeList.append(variant)

            # Check to see if correct reasoning but works
            for item in removeList:
                variable_feature.variants.remove(item)
            for item in addList:
                variable_feature.variant_derivations.append(item)

            if len(variable_feature.variants) > 1 or len(variable_feature.variant_derivations) > 0:
                continue # Leave as a variable feature
            else:
                variant = variable_feature.variants[0]
                if str(variant) not in combdev:
                    edited = True

                    # 1. Using the variable of the variable feature, find the local subcomponent in the template and retrieve the part number

                    localsub = doc.find(variable_feature.variable)

                    tempsub = sbol3.SubComponent(instance_of=variant, name=localsub.name, orientation=sbol3.SBOL_INLINE)

                    # Add the subcomponent to the template

                    template.features.append(tempsub)

                    # Change the constriant to the subcomponent

                    for constraint in template.constraints:
                        if constraint.subject == variable_feature.variable:
                            constraint.subject = tempsub.identity
                        if constraint.object == variable_feature.variable:
                            constraint.object = tempsub.identity

                    # Remove the localsubcomponent and the variable feature

                    template.features.remove(localsub)
                    obj.variable_features.remove(variable_feature)
            


        if edited:
            

            localsubs = [None] * 100 # Used for relabeling
            subs = [None] * 100 # subcomponents
            variableFeatures = {}
            copiedVariableFeatures = [None] * 100
            partsToFeatures = {}

            # Go through remaining variable features and create a dictionary with key = list of variants and value = part # of variants
            # From this, delete the variable features and add their copies back to their template
            # Then delete the original variable, and add the new variable based on the variants

            for variable_feature in list(obj.variable_features):
                variants = []
                for variant in variable_feature.variants:
                    variants.append(str(variant))
                variants = tuple(variants)

                # Now find the part number from the variable

                localsub = doc.find(variable_feature.variable)

                number = int(localsub.name.split(" ")[1])
                variableFeatures[variants] = number

                # Copy the variable features and add them to copiedVariableFeatures

                copyFeature = sbol3.VariableFeature(variants=variable_feature.variants, variant_derivations=variable_feature.variant_derivations, name=variable_feature.name, variable=variable_feature.variable, cardinality=variable_feature.cardinality)
                copiedVariableFeatures[number] = copyFeature

                # Remove the variable feature from the object

                obj.variable_features.remove(variable_feature)

                # Update the references


            # Add the copied variable features back to the template

            for var in copiedVariableFeatures:
                if var != None:
                    obj.variable_features.append(var)


            for feature in list(template.features):
                if type(feature) == sbol3.LocalSubComponent:
                    copyFeature = sbol3.LocalSubComponent(types=feature.types, name=feature.name, orientation=feature.orientation)
                    localsubs[int(feature.name.split(" ")[1])] = copyFeature
                    template.features.remove(feature)
                elif type(feature) == sbol3.SubComponent:
                    copyFeature = sbol3.SubComponent(instance_of=feature.instance_of, name=feature.name, orientation=feature.orientation)
                    subs[int(feature.name.split(" ")[1])] = copyFeature
                    template.features.remove(feature)
                

            for item in localsubs:
                if item != None:
                    template.features.append(item)

            for item in subs:
                if item != None:
                    template.features.append(item)

            # Fix variable features to reference the correct localsubcomponent

            for variable_feature in list(obj.variable_features):
                variants = []
                for variant in variable_feature.variants:
                    variants.append(str(variant))
                
                variants = tuple(variants)

                number = variableFeatures[variants]

                for feature in list(template.features):
                    if type(feature) == sbol3.LocalSubComponent:
                        if int(feature.name.split(" ")[1]) == number:
                            variable_feature.variable = feature.identity
                            break

            # Fix all of the constraints
            
            # Go through every subcomponent and localsubcomponent and do key: part #, value = displayID

            for feature in list(template.features):
                if type(feature) == sbol3.LocalSubComponent:
                    partsToFeatures[int(feature.name.split(" ")[1])] = feature.identity
                elif type(feature) == sbol3.SubComponent:
                    partsToFeatures[int(feature.name.split(" ")[1])] = feature.identity

            # Delete all constraints

            template.constraints.clear()

            # Add constraints one by one with part 1 being the subject and part 2 being the object until the end of the dictionary

            part = 1
            while part < len(partsToFeatures):
                constraint = sbol3.Constraint(restriction=sbol3.SBOL_MEETS, subject=partsToFeatures[part], object=partsToFeatures[part + 1])
                template.constraints.append(constraint)
                part += 1

            # Clear the part # from the subcomponents
            # Check this

            for feature in list(template.features):
                if type(feature) == sbol3.SubComponent:
                    del feature._properties[sbol3.SBOL_NAME]


    # For every object in Composite parts collection:

    return None


# Purpose: Update the uri references in the LinearDNAProducts to the _ins versions of the parts
# Input: SBOL3 document object
# Output: SBOL3 document object with updated references

def updateLinearDNAProducts(doc):
    # Go through every object in the doc
    # If it's a collection, then check if it's the LinearDNAProducts collection
    # For every member, get the identity, then replace it with the _ins version of the part
    
    for obj in doc.objects:
        if type(obj) == sbol3.Collection:
            if obj.display_id == 'LinearDNAProducts':
                tempList = []
                for member in obj.members:
                    mem = doc.find(member)
                    memberid = mem.identity
                    insConstruct = doc.find(memberid + "_ins")
                    displah_id = insConstruct.identity
                    tempList.append(displah_id)
                obj.members = tempList

    return doc


# Purpose: Update the collection names for basic parts and composite parts
# Input: SBOL3 document object
# Output: SBOL3 document object with updated collection names

def updateCollectionNames(doc):
    # Change the basic parts collection name to basicparts (if it exists)

    # Lists to go through to either add or take off of the document once completed
    removeList = []
    addList = []

    for obj in doc.objects:
        if type(obj) == sbol3.Collection:

            # Set the namespace for sbol3 so that the collections contain the correct namespace and are named correctly
            sbol3.set_namespace(obj.namespace)

            if obj.display_id == 'Basic_Parts':
                newCollection = sbol3.Collection(identity='BasicParts', name=obj.name, members=obj.members, description=obj.description)

                removeList.append(obj)
                addList.append(newCollection)

            elif obj.display_id == 'Composite_Parts':
                newCollection = sbol3.Collection(identity='CompositeParts', name=obj.name, members=obj.members, description=obj.description)

                removeList.append(obj)
                # Change components inside of the composite parts collection to their inserted construct if they have one

                removeMember = []

                for item in newCollection.members:
                    if doc.find(item + "_ins") != None:
                        removeMember.append(item)
                        newCollection.members.append(item + "_ins")

                for item in removeMember:
                    newCollection.members.remove(item)
                
                addList.append(newCollection)
    
    for item in removeList:
        doc.remove_object(item)

    for item in addList:
        doc.add(item)

    return doc

# Go through the objects in the document and if they don't have a description, then add a blank
# Input: Document object (sbol3)
# Output: Document object with updated descriptions
# NOT COMPLETE - NEED MORE SPECIFIC IMPLEMENTATION

def updateDescriptions(doc):

    for obj in doc.objects:
        if type(obj) == sbol3.Collection:
            for item in list(obj.members):
                temp = doc.find(item)
                if not temp:
                    continue

                if "_ins" in temp.name:
                    continue
                if temp.description == None:
                    if doc.find(item + "_ins") == None:
                        temp.description = ""
        
    return doc
                
            


# Purpose: To convert combinatorial derivation objects to component objects if necessary
# Input: SBOL3 file reference
# Output: SBOL3 file in new path, updated document object

def convCombDeriv(file_path_in):
    # read in the document as an rdf graph
    g = rdflib.Graph()
    result = g.parse(file_path_in)

    # Creating the Sbol document to be changed from the conversion
    doc = sbol3.Document()
    doc.read(file_path_in)

    # Get all objects from the graph
    dictionaryObj = doc._parse_objects(g)

    # Find all combinatorial derivation objects (identity: object)
    tempcombdev = {}
    combdev = {} 

    for item in dictionaryObj:
        if type(dictionaryObj[item]) == sbol3.CombinatorialDerivation:
            tempcombdev[item] = dictionaryObj[item]

    # 1. Check to see if the object has an inserted construct
    # Go through all combinatorial derivations - if has insert, remove insert from tempcombdev and add top level object to combdev
    for item in dictionaryObj:
        ins = item + "_ins"
        if ins in dictionaryObj:
            combdev[item] = dictionaryObj[item]
            tempcombdev.pop(item)
            if ins in tempcombdev:
                tempcombdev.pop(ins)


    # 2. Go through the remaining combinatorial derivation objects and check each variable feature to see if it has more than one variant
    for item in tempcombdev:
        temp = doc.find(item)
        for variable_feature in temp.variable_features:
            if len(variable_feature.variants) > 1:
                combdev[item] = dictionaryObj[item]
                break

    for item in combdev:
        if item in tempcombdev:
            tempcombdev.pop(item)

    # 3. Go through the remaining objects and check to see if their variable feature contains a combinatorial derivation variant
    for item in tempcombdev:
        temp = doc.find(item)
        for variable_feature in temp.variable_features:
            for variant in variable_feature.variants:
                if variant in combdev:
                    combdev[item] = tempcombdev[item]
                    break

    # Check if need to remove from tempcombdev after adding to combdev

    # 4. For every item in tempcombdev (Not a combinatorial derivation), convert it to a component

    newComponents = {}
    for item in tempcombdev:
        # From combinatorial derivation: name, displayId, namespace
        obj = doc.find(item)

        newComp = sbol3.Component(identity=obj.identity, types=sbol3.component.SBOL_COMPONENT)
        newComp.name = obj.name
        newComp.displayId = obj.display_id
        newComp.namespace = obj.namespace
        newComp.roles = [sbol3.SO_ENGINEERED_REGION]
        newComp.types = [sbol3.SBO_DNA]
        newComp.description = obj.description

        # From template: features, constraints, type
        template = doc.find(f'{obj.identity}_template')

        # Need to go through the subcomponents in order from the previous template
        # sort the subcomponents by the identity and then create a new list to run through it

        sortedSubcomponents = sorted(template.features, key=lambda x: x.identity)

        for feature in sortedSubcomponents:
            if type(feature) != sbol3.LocalSubComponent:
                subComp = sbol3.SubComponent(instance_of=feature.instance_of, orientation=feature.orientation)
                newComp.features.append(subComp)

        # Attempt to sort the constraints in the same way as subcomponents

        sortedConstraints = sorted(template.constraints, key=lambda x: x.identity)
            

        for constraint in sortedConstraints:
            newConstraint = sbol3.Constraint(constraint.restriction, constraint.subject.replace('_template', ''), constraint.object.replace('_template', ''))
            newConstraint.derived_from = constraint.derived_from
            newComp.constraints.append(newConstraint)

        newComponents[item] = newComp

    # 5. Delete the original combinatorial derivation object and template
    for item in tempcombdev:
        obj_doc = doc.find(item)
        doc.remove_object(obj_doc)

        template = doc.find(f'{item}_template')
        doc.remove_object(template)

    # 6. Add the new component object to the document
    for item in newComponents:
        doc.add(newComponents[item])

    # 7. Update the variable features in each of the combinatorial derivation objects if there are conversions
    # Might have to update to make sure that it's the correct logic (If there are any changes to combinatorial derivations)
    if tempcombdev != combdev:
        updateVariableFeatures(doc, combdev)

    # 8. Update the uri references
    # Not sure if this is necessary - doesn't seem to make a difference
    # Take a new dictionary mapping the identity of the old objects to the newly created components
    # Plug it into the helper function to update the uri refs (Not sure if does anything)
    
    oldToNew = {}

    for item in tempcombdev:
        oldToNew[tempcombdev[item].identity] = newComponents[item].identity

    h.update_uri_refs(doc, oldToNew)

    return doc



doc = convCombDeriv(file_path_in)
doc = updateLinearDNAProducts(doc)
doc = updateCollectionNames(doc)
doc = updateDescriptions(doc)

file_path_out = "two_backbones_ud.nt"
doc.write(file_path_out, file_format="sorted nt")
