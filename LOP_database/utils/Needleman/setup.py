from distutils.core import setup, Extension

modNeedle = Extension('needleman_chord_module', sources=['needleman_chord_module.c'])

setup(name='NeedlemanWunschChord',
      version='1.0',
      description='Optimization of the Needleman-Wunsch algorithm',
      ext_modules=[modNeedle])
