"""
Test case that checks the working of the utils/command/gen_uml.py module.
"""

from builtins import object
import os
import pkg_resources
import unittest

from utils.command.gen_uml import generate


class PseudoFile(object):
    def __init__(self):
        self.data = ""

    def write(self, data):
        self.data += data

    def close(self):
        pass


class GenUmlTestCase(unittest.TestCase):
    def test_loading(self):

        dist = pkg_resources.get_distribution("gaphor")
        model_file = os.path.join(dist.location, "tests/test-model.gaphor")
        outfile = PseudoFile()

        generate(model_file, outfile)

        assert outfile.data == GENERATED, '"""%s"""' % outfile.data


GENERATED = """# This file is generated by build_uml.py. DO NOT EDIT!

from gaphor.UML.properties import association, attribute, enumeration, derived, derivedunion, redefine
# class 'ValSpec' has been stereotyped as 'SimpleAttribute'
# class 'ShouldNotShowUp' has been stereotyped as 'SimpleAttribute' too
class Element(object): pass
class SubClass(Element): pass
class C(object): pass
class D(C): pass
C.attr = attribute('attr', 8cb780ba-3f11-11de-9595-00224128e79d, default=8cb7fd1a-3f11-11de-9595-00224128e79d, lower=8cb7c11a-3f11-11de-9595-00224128e79d, upper=8cb7df60-3f11-11de-9595-00224128e79d)
C.name1 = association('name1', SubClass, lower=602cb072-3bcb-11de-ac7f-00224128e79d, opposite='name2')
SubClass.name2 = association('name2', C, lower=602d56c6-3bcb-11de-ac7f-00224128e79d, opposite='name1')
C.base = association('base', SubClass, lower=e053585e-3bcc-11de-aa0c-00224128e79d, opposite='abstract')
D.subbase = association('subbase', SubClass, lower=f8d56502-3bcc-11de-aa0c-00224128e79d, opposite='concrete')
SubClass.concrete = association('concrete', D, lower=f8d5c998-3bcc-11de-aa0c-00224128e79d, upper=1665b18a-3bcd-11de-aa0c-00224128e79d, opposite='subbase')
D.name3 = association('name3', SubClass, lower=1af287dc-3bcd-11de-aa0c-00224128e79d, opposite='name4')
SubClass.abstract = derivedunion('abstract', C, e053abd8-3bcc-11de-aa0c-00224128e79d, f48f64a2-3bcc-11de-aa0c-00224128e79d, SubClass.concrete)
SubClass.name4 = redefine(SubClass, 'name4', D, name2)
"""

# # 'SubClass.value' is a simple attribute
# SubClass.value = attribute('value', str, lower=f9124094-3f14-11de-9595-00224128e79d)


# vim:sw=4:et:ai
