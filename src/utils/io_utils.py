import os

media_types = {'image': ['jpg', 'raf'], 'audio':['wav'], 'video':['mov', 'mp4']}

class ProjectTree:
    '''
    Holds all information about the project filetrees, starting from root.
    Provides functions for easy access and search of files
    '''
    
    def __init__(self, root):
        self._root = os.path.abspath(root)
        self._name = os.path.basename(self._root)
        self._subtrees = []
        self._file_paths = []
        
        self.update_tree()
                    
    def update_tree(self):
        self._subtrees = []
        self._file_paths = []
        for elem in sorted(os.listdir(self._root)):
            if os.path.isdir(self._root + '/' + elem):
                self._subtrees.append(ProjectTree(self._root + '/' + elem))
            else:
                if elem != '.DS_Store':
                    self._file_paths.append(self._root + '/' + elem)
        
    def get_name(self):
        return self._name
    
    def get_subtrees(self):
        return self._subtrees
    
    def get_file_paths(self):
        return self._file_paths
    
    def get_projects(self):
        if self._name == 'projects':
            return self._subtrees
        return None
        
    def get_media(self, media_type):
        media_subtypes = media_type.split('/', maxsplit=1)
        for subtree in self._subtrees:
            if subtree.get_name() == media_subtypes[0]:
                if len(media_subtypes) > 1:
                    return subtree.get_media(media_subtypes[1])
                else:
                    return subtree
        if len(media_subtypes) > 1 or self._name != media_subtypes[0]:
            return None
        else:
            return self._file_paths
        
    def make_dir(self, name):
        full_path = self._root + '/' + name
        
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            
        self.update_tree()
        return full_path
    
    def print_filetree(self, level=0):
        print('\t' * level + self._name + ':')
        for subdir in self._subtrees:
            subdir.print_filetree(level+1)
            
        for filepath in self._file_paths:
            print('\t' * (level+1) + filepath)
