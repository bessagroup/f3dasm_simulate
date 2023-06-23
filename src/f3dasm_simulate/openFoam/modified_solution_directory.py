from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import WriteParameterFile
from os import path


class ModifiedSolutionDirectory(SolutionDirectory):
    def writeDictionaryContents(self, directory, name, contents):
        """Writes the contents of a dictionary
        :param directory: Sub-directory of the case
        :param name: name of the dictionary file
        :param contents: Python-dictionary with the dictionary contents"""

        theDir = self.name
        if directory:
            theDir = path.join(theDir, directory)

        result = WriteParameterFile(path.join(theDir, name), noHeader=True)
        result.content = contents
        result.writeFile()
