#!/usr/bin/python
# coding: utf8
#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
from numpy  import *
import re
import TracesExtractor
from NeedlemanWunsch import *
from numpy.numarray.numerictypes import Float
from Sequencing.MessageGroup import MessageGroup
from Sequencing.Message import Message


#+---------------------------------------------- 
#| Upgma :
#|     Dedicated to the clustering
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class cluster:
    pass

def make_clusters(species):
    clusters = {}
    id = 1
    for s in species:
        c = cluster()
        c.id = id
        c.data = s
        c.size = 1
        c.height = 0
        clusters[c.id] = c
        id = id + 1
    return clusters

def find_min(clu, d):
    mini = None
    i_mini = 0
    j_mini = 0
    for i in clu:
        for j in clu:
            if j > i:
                tmp = d[j - 1 ][i - 1 ].getScore()
                if not mini:
                    mini = tmp
                if tmp <= mini:
                    i_mini = i
                    j_mini = j
                    mini = tmp
    return (i_mini, j_mini, mini)

def regroup(clusters, dist):
    i, j, dij = find_min(clusters, dist)
    ci = clusters[i]
    cj = clusters[j]
    # create new cluster
    k = cluster()
    k.id = max(clusters) + 1
    k.data = (ci, cj)
    k.size = ci.size + cj.size
    k.height = dij / 2.
    # remove clusters
    del clusters[i]
    del clusters[j]
    # compute new distance values and insert them
    dist.append([])
    for l in range(0, k.id - 1):
        dist[k.id - 1].append(0)
    for l in clusters:
        dil = dist[max(i, l) - 1][min(i, l) - 1]
        djl = dist[max(j, l) - 1][min(j, l) - 1]
        dkl = (dil * ci.size + djl * cj.size) / float (ci.size + cj.size)
        dist[k.id - 1][l - 1] = dkl
    # insert the new cluster
    clusters[k.id] = k

    if len(clusters) == 1:
        # we're through !
        return clusters.values()[0]
    else:
        return regroup(clusters, dist)

def pprint(tree, len):
    if tree.size > 1:
        # it's an internal node
        print "("
        pprint(tree.data[0], tree.height)
        print ","
        pprint(tree.data[1], tree.height)
        print ("):%2.2f" % (len - tree.height))
    else :
        # it's a leaf
        print ("%s:%2.2f" % (tree.data, len))

def test():
    species = [ "A", "B", "C", "D", "E" ]
    matr = [ [ 0., 4., 5., 5., 2. ],
             [ 4., 0., 3., 5., 6. ],
             [ 5., 3., 0., 2., 5. ],
             [ 5., 5., 2., 0., 3. ],
             [ 2., 6., 5., 3., 0. ] ]
    clu = make_clusters(species)
    tree = regroup(clu, matr)
    pprint(tree, tree.height)


def test2():
    species = [ "Turtle", "Man", "Tuna", "Chicken",
                "Moth", "Monkey", "Dog" ]
    matr = [ [], [ 19 ], [ 27, 31 ],
             [ 8, 18, 26 ], [ 33, 36, 41, 31 ],
             [ 18, 1, 32, 17, 35 ], [ 13, 13, 29, 14, 28, 12 ] ]
    clu = make_clusters(species)
    tree = regroup(clu, matr)
    pprint(tree, tree.height)


                  
                 
                                                        
          
          
#+---------------------------------------------- 
#| UNIT TESTS
#+----------------------------------------------
if __name__ == "__main__":
    sequence1 = "bonjour  where  you o!"
    sequence2 = "bonjour me where will you go!"
    sequence3 = "bonjour tii where do you come from!"
    sequence4 = "bonsoir aaaaaaaa, your are not welcome in my world on 192.168.0.10"
    sequence5 = "bonsoir bbbbbb, your are not welcome in my world on 10.12.131.12"
    sequence6 = "bonsoir ccccccc, your are not welcome in my world on 85.45.56.96"
    sequences = []
    
    alignor = NeedlemanWunsch()
    sequences.append(alignor.asctohex(sequence1))
    sequences.append(alignor.asctohex(sequence2))
    sequences.append(alignor.asctohex(sequence3))
    sequences.append(alignor.asctohex(sequence4))
    sequences.append(alignor.asctohex(sequence5))
    
    taille = len(sequences)
    clusters = []
    
    for i in range(0, taille) :
        line_groups = []
        for j in range(0, taille) :
            sequence_i = sequences[i]
            sequence_j = sequences[j]
            msg_i = Message()
            msg_i.setData(sequence_i)
            msg_j = Message()
            msg_j.setData(sequence_j)
            group = MessageGroup(str(i) + ";" + str(j), [msg_i, msg_j])
            group.computeRegex()
            group.computeScore()
            line_groups.append(group)
            
        clusters.append(line_groups)
            
    print clusters
##        clusters.append(cluster_line)
#    matr = [ [ 0., 4., 5., 5., 2. ],
#             [ 4., 0., 3., 5., 6. ],
#             [ 5., 3., 0., 2., 5. ],
#             [ 5., 5., 2., 0., 3. ],
#             [ 2., 6., 5., 3., 0. ] ]
    clu = make_clusters(sequences)
    tree = regroup(clu, clusters)
    pprint(tree, tree.height)
#    sequence1 = "bonjour you where do you come from!"
#    #sequence1 = "bonjour *(you|me) where *(do|will) you *(c|g)o*(me from)!"
#    #sequence1 = "bonjour *(you|me)*(me) where *(do|will)*(will) you *(c|g)*(g)o*(me from)!"
#    #sequence1 = "bonjour  where  you o!"
#    sequence2 = "bonjour me where will you go!"
#    sequence3 = "bonjour tii where do you come from!"
#    sequence4 = "bonsoir aaaaaaaa, your are not welcome in my world on 192.168.0.10"
#    sequence5 = "bonsoir bbbbbb, your are not welcome in my world on 10.12.131.12"
#    sequence6 = "bonsoir ccccccc, your are not welcome in my world on 85.45.56.96"
#    sequences = []
#    
#    alignor = NeedlemanWunsch()
#    sequences.append(alignor.asctohex(sequence1))
#    sequences.append(alignor.asctohex(sequence2))
#    sequences.append(alignor.asctohex(sequence3))
#    sequences.append(alignor.asctohex(sequence4))
#    sequences.append(alignor.asctohex(sequence5))
#    
#    sequences.append("d901ffffbe8512cd2c00ff020100000000d533012805000000c00000020000000000000000000000881300000200000002000000")
#    sequences.append("cc01ffffc98512cd2c00ff0201000000bf9874012805010000c00000020000000000000000000000881300000200000002000000")
#    sequences.append("d901ffffef8612cd2c00ff020100000000d533012805000000c00000020000000000000000000000881300000200000002000000")
#    sequences.append("cc01ffff048712cd2c00ff0201000000bf9874012805010000c00000020000000000000000000000881300000200000002000000")
#    sequences.append("d902000048e29fda1400ff0102000000f7dac70001000000be8512cd3400ff0301000000080532012805f30000c00000020000000000000000000000881300000200000002000000dbb20e50f7d7ce8a")
#    sequences.append("d901f300378712cd1400ff0101000000bf9874000100000048e29fda")
#    sequences.append("cc02010054e29fda1400ff01020000000070b10001000000c98512cd3400ff0301000000080509012805ec0100c00000020000000000000000000000881300000200000002000000dbb20e50f7dbce8a")
#    sequences.append("d901f300478712cd0c00ff040200000000966701")
#    sequences.append("cc01ec01478712cd1400ff0102000000009667000100000054e29fda")
#    sequences.append("cc01ec014f8712cd0c00ff04020000000043a201")
#    sequences.append("4301fffff48912cd2c00ff0201000000000000012805000000c00000020000000000000000000000881300000200000002000000")
#    sequences.append("4301ffff248b12cd2c00ff0201000000000000012805000000c00000020000000000000000000000881300000200000002000000")
#    sequences.append("43020000586d9dda1400ff01010000000976c80001000000f48912cd3400ff03010000000976c8012805a90028050000020000000f0000001f000000881300000200000002000000dbb20e500011440f")
#    sequences.append("4301a900a28b12cd1400ff01010000000000000001000000586d9dda")
#    sequences.append("4301a900b18b12cd5200010601000000000000010e504600b69adb3220b7323de03a57237a76469ebd2f1583b33de8332efd2c13849d4bcb24ba19182ad554a802c19562471dafcec52a26d85d7018f002fd75b8b7b715d5")
#    sequences.append("43010000846e9dda3400ff03010000000976c8012805a90028050000020000000f0000001f000000881300000200000002000000dbb20e500011440f")
#    sequences.append("4301a900b88c12cd1400ff01010000000000000001000000846e9dda")
#    sequences.append("4301a9004a8d12cd5200010601000000000000010e504600b69adb3220b7323de03a57237a76469ebd2f1583b33de8332efd2c13849d4bcb24ba19182ad554a802c19562471dafcec52a26d85d7018f002fd75b8b7b715d5")
#    sequences.append("430100001a6f9dda14000101010000000976c80001000000b18b12cd")
#    sequences.append("430100001d6f9ddaa203010601000000000000010e509603b69adb322aa2323d994eae6038abb858c7b13f954c53efb0aea51be4f23c9268588c94dd741509a26036bda6823cd98f7d8f2b9a0773068657e0a9f363bad6ddbb045a66806f9fa8367a22ac1ec78fd1ad225d207f2e63cede503372ca27ba5c706eb2224e85bc3b29726a7207732db457e0a9f363bad6ddbb045a66806f9fa8367a22acb5078fd1fda8045b7f2ec5e3de503372ca27ba5c706eb2220921bc3b096ee42225c83af15d8e9389944a62862c86114f171ec3a8deb2d6ba15b8f9d58ae53ffd9a6eed3b86c20049ca270a04706eb222e76abc3bc2d1c61a903965f02bbf3ea2572a6cf04569d10dd8598366d7cf3ce5bb9674a914aa58dc0223b6f22fda9a74ca27180c706eb22232f0bc3b46ca5d945ed067e9fed658537513fb4c358b92c2c65d1b9f48006dcd98a2c0c81245e44f3631e3259d0a7c62ca270597706eb222e4d5bc3b649668c3049ca8d1ef11f5a66abdd05d377b0adf672114416608aca932f65e87f627609ff319636fcb4f27dfca278b69706eb222b0b1bc3b83083474535d35c54eeb408004b627570a6bc95d5eaa4a4dc7ba40ef1f6aec1005625a2d63ab641a0c019b7fca27136d706eb2225e45bc3b65fbf8a8713fe99680a72c2742990949e07202621f08b6ce2ecaead2a4138f3b50ed9111bef8bffa991703cbca279655706eb222efd5bc3b95f8d653218048416dcf66651fd996cb38d8af435a9570982a1d9492cb3de79c91cdfd860c8bcf63535e1144ca27c4db706eb2227c35bc3b7812095848d6419f63d715d5e73782fc957b8a055b2c27f2afae1c54ce324be434d3673ca9a2aae53d9a907dca27632b706eb2221195bc3b06d44c0a272f7689445b93cf3b6abd7efbaca85a78ee0ef6cc9094f81ed28708f2b935a1e46e80fda0abf49eca27c35f706eb222e94ebc3bea0c99180031be08450b1421546045ddecae990a715b948cc985becc61451b020dab0fe8a55126e7bd746186ca27969d706eb2224b76bc3b8e6588a25357e8c652998d8c27c5f87c4df9f57c10d1675e68c5f81ff15c5b62906aef759f771d89392563e39eb808f5465e47481df03d44996a806d1f3e8ec51a7e9ba5557e41701dea1a20ce43c3ea0e8a981d340f5b55fa988686b5aa2a83c74e7a4e97b781d3965af20525cccd3cf44751bf84a4299824ad8f51d16f5c30bad8ac54c7ae8d667eb568e9799b4967dc78705e02fc4c1d05b18645ca279e4a706eb222885fbc3b1059cc211a0630575a65d065e7fabf48bfffd4d7b7b77a270000b7b7")
#    sequences.append("430100001d6f9dda0c00ff04020000005710fc01")
#    sequences.append("4302a9004a8d12cd140001010100000000000000010000001d6f9dda1400ff010000000000000000020000001d6f9dda")
    
#    sequences.append(alignor.asctohex(sequence6))
    
    # put the clusters in this table
#    
#    taille = len(sequences) - 1
#    clusters = zeros([taille, taille], MessageGroup)
#    
#    for i in range(0, taille) :
#        for j in range(0, taille) :
#            if (i != j) :
#                sequence_i = sequences[i]
#                sequence_j = sequences[j]
#                msg_i = Message()
#                msg_i.setData(sequence_i)
#                msg_j = Message()
#                msg_j.setData(sequence_j)
#                group = MessageGroup(str(i) + ";" + str(j), [msg_i, msg_j])
#                group.computeRegex()
#                group.computeScore()
#                clusters[i][j] = group
##        clusters.append(cluster_line)
#        
#    print str(clusters)
#    
#    upgma = Upgma()
#    # search the highest similarity
#    (i_max, j_max, maxi) = upgma.getMaximumSimilary(clusters, taille)
#    print "Will fusion the line {0} with {1}".format(str(i_max), str(j_max))
#    (clusters, taille) = upgma.fusion(i_max, j_max, clusters, taille)
