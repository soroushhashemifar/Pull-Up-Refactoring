from antlr4 import *

from qualitymeter.gen.javaLabeled.JavaLexer import JavaLexer
from qualitymeter.gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from qualitymeter.gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener
import itertools


class pullUpListener(JavaParserLabeledListener):

    def __init__(self):
        self.__classes = []
        self.__parent_and_child_classes = {}
        self.__methods_of_classes = {}
        self.__number_of_classes = 0
        self.__current_class_or_interface = None

    @property
    def get_methods_and_classes(self):
        return self.__methods_of_classes

    @property
    def get_parents_and_children(self):
        return self.__parent_and_child_classes

    def enterClassDeclaration(self, ctx:JavaParserLabeled.ClassDeclarationContext):
        """

        :param ctx:
        :return:
        """

        # self.__number_of_classes += 1
        self.__current_class_or_interface = ctx.IDENTIFIER().getText()
        self.__classes.append(ctx.IDENTIFIER().getText())
        self.__methods_of_classes[self.__current_class_or_interface] = []

        if ctx.EXTENDS() is not None and ctx.typeType().getText() in self.__classes:
            self.__parent_and_child_classes[ctx.IDENTIFIER().getText()] = ctx.typeType().getText()

        elif ctx.IMPLEMENTS() is not None and ctx.typeList().getText() in self.__classes:
            self.__parent_and_child_classes[ctx.IDENTIFIER().getText()] = ctx.typeList().getText()

    def enterInterfaceDeclaration(self, ctx:JavaParserLabeled.InterfaceDeclarationContext):
        """

        :param ctx:
        :return:
        """
        self.__number_of_classes += 1
        self.__current_class_or_interface = ctx.IDENTIFIER().getText()
        self.__classes.append(ctx.IDENTIFIER().getText())
        self.__methods_of_classes[self.__current_class_or_interface] = []

        if ctx.EXTENDS() is not None and ctx.typeList().getText() in self.__classes:
            self.__parent_and_child_classes[ctx.IDENTIFIER().getText()] = ctx.typeList().getText()

    def enterMethodDeclaration(self, ctx: JavaParserLabeled.MethodDeclarationContext):
        """

        :param ctx:
        :return:
        """
        self.__methods_of_classes[self.__current_class_or_interface].append(ctx.IDENTIFIER().getText())

    def get_pullups(self):
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
            for classes_tuple in list(itertools.combinations(value, 2)):
                methods1 = set(self.get_methods_and_classes[classes_tuple[0]])
                methods2 = set(self.get_methods_and_classes[classes_tuple[1]])
                parents_methods = set(self.get_methods_and_classes[key])
                methods_to_refactor_ = list(methods1.intersection(methods2) - parents_methods)
            
                if len(methods_to_refactor_) != 0:
                    methods_to_refactor.extend(methods_to_refactor_)

            methods_to_refactor = list(set(methods_to_refactor))
            if len(methods_to_refactor) != 0:
                class_methods_to_refactor[key] = methods_to_refactor

        return class_methods_to_refactor


stream = FileStream("/home/soroushh/Downloads/test.java", encoding='utf-8')
lexer = JavaLexer(stream)
token_stream = CommonTokenStream(lexer)
parser = JavaParserLabeled(token_stream)
parse_tree = parser.compilationUnit()
walker = ParseTreeWalker()
pu_listener = pullUpListener()
walker.walk(t=parse_tree, listener=pu_listener)

print(pu_listener.get_pullups())
