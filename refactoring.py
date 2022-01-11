from antlr4 import *

from qualitymeter.gen.javaLabeled.JavaLexer import JavaLexer
from qualitymeter.gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from qualitymeter.gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener
import itertools
import os


class pullUpListener(JavaParserLabeledListener):
    
    """
    This class investigate the situations for PullUp refactoring between 
    prent classes and inherited ones.
    """

    def __init__(self):
        self.__classes = []
        self.__parent_and_child_classes = {}
        self.__methods_of_classes = {}
        self.__current_class_or_interface = None

    @property
    def get_methods_and_classes(self):
        """
        This method is the getter of __methods_of_classes.

        :param:
        :return: a dictionary of methods belong to each class
        """
        
        return self.__methods_of_classes

    @property
    def get_parents_and_children(self):
        """
        This method is the getter of __parent_and_child_classes.

        :param:
        :return: a dictionary of parent of each class
        """
        
        return self.__parent_and_child_classes

    def enterClassDeclaration(self, ctx:JavaParserLabeled.ClassDeclarationContext):
        """
        This method add the current class, its parent to the proper dictionary.

        :param: context of ClassDeclarationContext
        :return: None
        """

        self.__current_class_or_interface = ctx.IDENTIFIER().getText()
        self.__classes.append(ctx.IDENTIFIER().getText())
        self.__methods_of_classes[self.__current_class_or_interface] = []

        if ctx.EXTENDS() is not None and ctx.typeType().getText() in self.__classes:
            self.__parent_and_child_classes[ctx.IDENTIFIER().getText()] = ctx.typeType().getText()

        elif ctx.IMPLEMENTS() is not None and ctx.typeList().getText() in self.__classes:
            self.__parent_and_child_classes[ctx.IDENTIFIER().getText()] = ctx.typeList().getText()

    def enterInterfaceDeclaration(self, ctx:JavaParserLabeled.InterfaceDeclarationContext):
        """
        This method add the current class, its parent to the proper dictionary.

        :param: context of InterfaceDeclarationContext
        :return: None
        """
        
        self.__current_class_or_interface = ctx.IDENTIFIER().getText()
        self.__classes.append(ctx.IDENTIFIER().getText())
        self.__methods_of_classes[self.__current_class_or_interface] = []

        if ctx.EXTENDS() is not None and ctx.typeList().getText() in self.__classes:
            self.__parent_and_child_classes[ctx.IDENTIFIER().getText()] = ctx.typeList().getText()

    def enterMethodDeclaration(self, ctx: JavaParserLabeled.MethodDeclarationContext):
        """
        This method add the methods of the current class to the proper dictionary.

        :param: context of MethodDeclarationContext
        :return: None
        """
        
        self.__methods_of_classes[self.__current_class_or_interface].append(ctx.IDENTIFIER().getText())

    def get_pullups(self):
        """
        This method collects the situations of pullups and return them as a dictionary,
        where keys represent the class and values represent a list of methods that must be pulled up.

        :param: None
        :return: a dictionary of class-methods
        """
        
        # Collecting a dictionary of classes and their children.
        parent_children = {}
        for classname in set(self.get_parents_and_children.values()):
            children = parent_children.get(classname, [])
            for key, value in self.get_parents_and_children.items():
                if value == classname:
                    children.append(key)

            parent_children[classname] = children
            
        class_methods_to_refactor = {}
        for key, value in parent_children.items():
            methods_to_refactor = []
            # Getting intersection of methods between each pair of children of a class,
            # so we can collect the common methods between them
            for classes_tuple in list(itertools.combinations(value, 2)):
                methods1 = set(self.get_methods_and_classes[classes_tuple[0]])
                methods2 = set(self.get_methods_and_classes[classes_tuple[1]])
                parents_methods = set(self.get_methods_and_classes[key])
                methods_to_refactor_ = list(methods1.intersection(methods2) - parents_methods)
            
                if len(methods_to_refactor_) != 0:
                    methods_to_refactor.extend(methods_to_refactor_)

            # The class is considered only if there is any common method among its children
            methods_to_refactor = list(set(methods_to_refactor))
            if len(methods_to_refactor) != 0:
                class_methods_to_refactor[key] = methods_to_refactor

        return class_methods_to_refactor

    
def get_all_filenames(walk_dir, valid_extensions):
    """get all files of a directory
    Args:
        walk_dir ([type]): [description]
        valid_extensions ([type]): [description]
    Yields:
        [type]: [description]
    """
    for root, sub_dirs, files in os.walk(walk_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if any([file_name.endswith(extension) for extension in valid_extensions]) and "test" not in file_path:
                yield file_path
                

if __main__ == "__name__":
    walk_dir = "path\\of\\directory"
    valid_extensions = ['.java']
    
    for file_name in get_all_filenames(walk_dir, valid_extensions):
        stream = FileStream(file_name, encoding='utf-8')
        lexer = JavaLexer(stream)
        token_stream = CommonTokenStream(lexer)
        parser = JavaParserLabeled(token_stream)
        parse_tree = parser.compilationUnit()
        walker = ParseTreeWalker()
        pu_listener = pullUpListener()
        walker.walk(t=parse_tree, listener=pu_listener)

        print(file_name, "\n", pu_listener.get_pullups())
