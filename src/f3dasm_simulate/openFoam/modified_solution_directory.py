from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import WriteParameterFile
from os import path


class ModifiedSolutionDirectory(SolutionDirectory):
    def writeDictionaryContents(self, directory, name, contents):
        """
        Extend the pyFoam class to write the dictionary file without header which
        can cause issues when parsing the parameter file.

        Parameters
        ----------
        directory : Sub-directory of the case
        name : name of the dictionary file
        contents : Python-dictionary with the dictionary contents
        """
        theDir = self.name
        if directory:
            theDir = path.join(theDir, directory)

        result = WriteParameterFile(path.join(theDir, name), noHeader=True)
        result.content = contents
        result.writeFile()
