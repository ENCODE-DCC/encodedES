# Module downloads, parses all ontology files and indexes them in Elastic Search
# Note: This is the basic version
import networkx as nx

from pyelasticsearch import ElasticSearch
from urllib2 import Request, urlopen

uberonURL = "http://svn.code.sf.net/p/obo/svn/uberon/trunk/composite-vertebrate.obo"
urls = [uberonURL]

#make connection to elastic search
connection = ElasticSearch('http://localhost:9200')

index_name = "ontology-tree"
doc_type_name = "basic"


def getTerm(stream):
    ''' Get GO term block from the obo file'''

    block = []
    for line in stream:
        if line.strip() == "[Term]" or line.strip() == "[Typedef]":
            break
        else:
            if line.strip() != "":
                block.append(line.strip())

    return block


def parseTagValue(term):
    ''' Get tag-value pairs of each GO Term '''

    data = {}
    for line in term:
        tag = line.split(': ', 1)[0]
        value = line.split(': ', 1)[1]
        if not tag in data:
            data[tag] = []
        data[tag].append(value)

    return data


def getDescendents(goid):
    ''' Get Descendents of Go Term '''

    recursiveArray = [goid]
    if goid in terms:
        children = terms[goid]['children']
        if len(children) > 0:
            for child in children:
                recursiveArray.extend(getDescendents(child))

    return set(recursiveArray)


def getAncestors(goid):
    ''' Get Ancestors of GO ID '''

    recursiveArray = [goid]
    if goid in terms:
        parents = terms[goid]['parents']
        if len(parents) > 0:
            for parent in parents:
                recursiveArray.extend(getAncestors(parent))

    return set(recursiveArray)


def iterativeChildren(nodes):
    ''' Traverse the tree for the give set of nodes'''

    results = []
    while 1:
        newNodes = []
        if len(nodes) == 0:
            break
        for node in nodes:
            results.append(node)
            if terms[node]['data']:
                for child in terms[node]['data']:
                    if child not in results:
                        newNodes.append(child)
        nodes = newNodes
    return results


def getDevelopmentSlims(goid):
    ''' Get Developmental Slims '''

    slims = []
    slimTerms = {
        'UBERON:0003263': 'mesoderm',
        'UBERON:0000924': 'ectoderm',
        'UBERON:0000925': 'endoderm'
    }
    for slimTerm in slimTerms:
        if slimTerm in terms[term]['closure']:
            slims.append(slimTerms[slimTerm])
    return slims


def getSystemSlims(goid):
    ''' Get System Slims '''

    slims = []
    slimTerms = {
        'UBERON:0000383': 'musculature of body',
        'UBERON:0000949': 'endocrine system',
        'UBERON:0000990': 'reproductive system',
        'UBERON:0001004': 'respiratory system',
        'UBERON:0001007': 'digestive system',
        'UBERON:0001008': 'excretory system',
        'UBERON:0001009': 'circulatory system',
        'UBERON:0001434': 'skeletal system',
        'UBERON:0002405': 'immune system',
        'UBERON:0002416': 'integumental system',
        'UBERON:0001032': 'sensory system',
        'UBERON:0001017': 'central nervous system',
        'UBERON:0000010': 'peripheral nervous system'
    }
    for slimTerm in slimTerms:
        if slimTerm in terms[term]['closure']:
            slims.append(slimTerms[slimTerm])
    return slims


def getOrganSlims(goid):
    ''' Get Organ Slims '''

    slims = []
    slimTerms = {
        'UBERON:0002369': 'adrenal gland',
        'UBERON:0002110': 'gallbladder',
        'UBERON:0002106': 'spleen',
        'UBERON:0001173': 'billary tree',
        'UBERON:0001043': 'esophagus',
        'UBERON:0000004': 'nose',
        'UBERON:0000056': 'ureter',
        'UBERON:0000057': 'urethra',
        'UBERON:0000059': 'large intestine',
        'UBERON:0000165': 'mouth',
        'UBERON:0000945': 'stomach',
        'UBERON:0000948': 'heart',
        'UBERON:0000955': 'brain',
        'UBERON:0000970': 'eye',
        'UBERON:0000991': 'gonad',
        'UBERON:0001043': 'esophagus',
        'UBERON:0001255': 'urinary bladder',
        'UBERON:0001264': 'pancreas',
        'UBERON:0001474': 'bone element',
        'UBERON:0002003': 'peripheral nerve',
        'UBERON:0002048': 'lung',
        'UBERON:0002097': 'skin of body',
        'UBERON:0002107': 'liver',
        'UBERON:0000059': 'large intestine',
        'UBERON:0002108': 'small intestine',
        'UBERON:0002113': 'kidney',
        'UBERON:0002240': 'spinal cord',
        'UBERON:0002367': 'prostate gland',
        'UBERON:0002370': 'thymus',
        'UBERON:0003126': 'trachea',
        'UBERON:0001723': 'tongue',
        'UBERON:0001737': 'larynx',
        'UBERON:0006562': 'pharynx',
        'UBERON:0001103': 'diaphragm',
        'UBERON:0002185': 'bronchus',
        'UBERON:0000029': 'lymph node',
        'UBERON:0002391': 'lymph',
        'UBERON:0010133': 'neuroendocrine gland',
        'UBERON:0001132': 'parathyroid gland',
        'UBERON:0002046': 'thyroid gland',
        'UBERON:0001981': 'blood vessel',
        'UBERON:0001473': 'lymphatic vessel',
        'UBERON:0000178': 'blood',
        'UBERON:0002268': 'olfactory organ',
        'UBERON:0007844': 'cartilage element',
        'UBERON:0001690': 'ear',
        'UBERON:0001987': 'placenta',
        'UBERON:0001911': 'mammary gland',
        'UBERON:0001630': 'muscle organ',
        'UBERON:0000007': 'pituitary gland',
        'UBERON:0002370': 'thymus',
        'UBERON:0000478': 'extraembryonic structure'
    }
    for slimTerm in slimTerms:
        if slimTerm in terms[term]['closure']:
            slims.append(slimTerms[slimTerm])
    return slims


#counter for indexing this is used as ID in elastic search
counter = 0

print "Starting...."
print

terms = {}
root_terms = ['UBERON:0000000', 'UBERON:0001062', 'CL:0000000', 'CL:0000344', 'CHEBI:50906', 'CHEBI:24431', 'CHEBI:36342', 'GO:0003674', 'GO:0005575', 'GO:0008150', 'IAO:0000030', 'PATO:0000001', 'PR:000018263', 'NCBITaxon:1']
term_prefixs = ['UBERON', 'CL', 'CHEBI', 'GO', 'IAO', 'PATO', 'PR', 'NCBITaxon']
stupid_terms = []

for url in urls:

    req = Request(url)

    print "downloading - " + url
    oboFile = urlopen(req)

    #skip the file header lines
    print "parsing ontology - " + url
    getTerm(oboFile)

    #infinite loop to go through the obo file.
    #Breaks when the term returned is empty, indicating end of file
    while 1:
        #get the term using the two parsing functions
        term = parseTagValue(getTerm(oboFile))
        if len(term) != 0:
            if (term['id'][0]).find(':') != -1:
                if ((term['id'][0]).split(':'))[0] in term_prefixs:
                    try:
                        termID = term['id'][0]
                        termName = ''
                        try:
                            termName = term['name'][0]
                        except KeyError:
                            pass

                        if 'is_a' in term:
                            termParents = [p.split()[0] for p in term['is_a']]

                            if not termID in terms:
                                terms[termID] = {'id': '', 'name': '', 'parents': [], 'children': [], 'part_of': [], 'develops_from': [], 'organs': [], 'closure': [], 'slims': [], 'data': []}

                            #append termID and termName to the dict
                            terms[termID]['id'] = termID
                            terms[termID]['name'] = termName

                            #for every parent term, add this current term as children
                            for termParent in termParents:
                                if (termParent.split(':'))[0] in term_prefixs:
                                    if termParent != 'CL:0000812':
                                        terms[termID]['parents'].append(termParent)
                                        if not termParent in terms:
                                            terms[termParent] = {'parents': [], 'children': [], 'part_of': [], 'develops_from': [], 'organs': [], 'closure': [], 'slims': [], 'data': []}
                                        terms[termParent]['children'].append(termID)

                            # Handling relationships for each ontology term
                            if 'relationship' in term:
                                relations = [p.split()[0] for p in term['relationship']]
                                relationTerms = [p.split()[1] for p in term['relationship']]
                                relationCheck = []
                                for p in term['relationship']:
                                    try:
                                        relationCheck.append(p.split()[2])
                                    except:
                                        relationCheck.append("N/A")
                                count = 0
                                relationships = ['part_of', 'develops_from']
                                for relation in relations:
                                    if relation in relationships:
                                        if relationTerms[count] != 'CL:0000812':
                                            if ((relationTerms[count]).split(':'))[0] in term_prefixs:
                                                if relationCheck[count] == '!' or 'NCBITaxon:9606' in relationCheck[count] or 'source' in relationCheck[count]:
                                                    terms[termID][relation].append(relationTerms[count])
                                    count = count + 1
                        else:
                            if term['id'][0] not in terms:
                                terms[termID] = {'id': '', 'name': '', 'parents': [], 'children': [], 'part_of': [], 'develops_from': [], 'organs': [], 'closure': [], 'slims': [], 'data': []}
                                #append termID and termName to the dict
                                terms[termID]['id'] = termID
                                terms[termID]['name'] = termName
                            else:
                                terms[termID]['id'] = termID
                                terms[termID]['name'] = termName
                    except KeyError:
                        stupid_terms.append(termID)
        else:
            break

# Deleting all useless, time wasting terms
for stupid_term in stupid_terms:
    try:
        del(terms[stupid_term])
    except KeyError:
        pass

useless = []
for term in terms:
    try:
        terms[term]['id']
    except:
        useless.append(term)

for useL in useless:
    del(terms[useL])

print "Take a break, I have to calculate closures for " + str(len(terms)) + " ontology terms and index them in elasticsearch. Long operation. Sigh!!"

for term in terms:
    terms[term]['data'] = list(set(terms[term]['parents']) | set(terms[term]['part_of']))

G = nx.DiGraph()

for term in terms:
    words = iterativeChildren(terms[term]['data'])
    for word in words:
        terms[term]['closure'].append(word)
    for parent in terms[term]['parents']:
        G.add_edge(term, parent, r='is_a')
    for part in terms[term]['part_of']:
        G.add_edge(term, part, r='part_of')

count = 0

# Probably the most important part of the module.
# This loop calculates the edges for each tree and indexes them in elasticsearch
for term in terms:
    for c in terms[term]['closure']:
        tree = {}
        tree['source'] = term
        tree['source_name'] = terms[term]['name']
        tree['target'] = c
        tree['target_name'] = terms[c]['name']
        tree['links'] = []
        for path in nx.all_simple_paths(G, source=term, target=c):
            for p in path:
                if len(path) - 1 != path.index(p):
                    link = {}
                    link['s'] = {p: terms[p]['name']}
                    link['t'] = {path[path.index(p) + 1]: terms[path[path.index(p) + 1]]['name']}
                    link['type'] = G.get_edge_data(p, path[path.index(p) + 1])['r']
                    if link not in tree['links']:
                        tree['links'].append(link)
        if count % 5000 == 0:
            connection.index(index_name, doc_type_name, tree, id=count)
            connection.flush(index=index_name)
        connection.refresh()
        count = count + 1
