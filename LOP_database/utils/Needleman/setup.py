from distutils.core import setup, Extension

modNeedle = Extension('needleman_chord', sources=['needleman_chord.c'])

setup(name='PackageName',
      version='1.0',
      description='Optimization of the Needleman-Wunsch algorithm',
      ext_modules=[modNeedle])
