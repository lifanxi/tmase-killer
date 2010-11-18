#! /usr/bin/python

from docclass import *

c = fisherclassifier(getwords)
c.setdb('/tmp/db.db')
f = open('text', 'r')
txt = f.read()
c.train(txt, 'good')
f.close()
c.train('Nobody owns the water.','bad')
c.train('the quick rabbit jumps fences','bad')
c.train('buy pharmaceuticals now','bad')
c.train('make quick money at the online casino','bad')
c.train('the quick brown fox jumps','bad')

#print c.fprob('splx', 'good')
#print c.fprob('case', 'good')
#print c.fprob('abcd', 'good')
print c.classify('splx case study')
print c.classify('brown nobody jumps seg owner')
