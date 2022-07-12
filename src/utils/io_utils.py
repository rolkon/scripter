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
        self._file_names = []
        
        self.update_tree()
        
    def get_name(self):
        return self._name
    
    def get_root(self):
        return self._root
    
    def get_subtrees(self):
        return self._subtrees
    
    def get_file_paths(self):
        return self._file_paths
    
    def get_file_names(self):
        return self._file_names
    
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
        
        
    def make_media(self, media_type):
        full_path = self._root + '/' + media_type
        
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            
        self.update_tree()
        
        return self.get_media(media_type)
    
    def update_tree(self):
        self._subtrees = []
        self._file_paths = []
        for elem in sorted(os.listdir(self._root)):
            if os.path.isdir(self._root + '/' + elem):
                self._subtrees.append(ProjectTree(self._root + '/' + elem))
            else:
                if elem != '.DS_Store':
                    self._file_paths.append(self._root + '/' + elem)
                    self._file_names.append(elem.split('.')[0])
    
    def is_empty(self):
        if len(self._subtrees) == 0 and len(self._file_paths) == 0:
            return True
        else:
            return False
        
    def prune_tree(self):
        for sub_tree in list(self._subtrees):
            sub_tree.prune_tree()
            
        self.update_tree()
            
        if self.is_empty():
            print('deleting', self._root)
            if os.path.exists(self._root + '/.DS_Store'):
                os.remove(self._root + '/.DS_Store')
            os.rmdir(self._root)
    
    def print_filetree(self, level=0):
        print('\t' * level + self._name + ':')
        for subdir in self._subtrees:
            subdir.print_filetree(level+1)
            
        for filepath in self._file_paths:
            print('\t' * (level+1) + filepath)
