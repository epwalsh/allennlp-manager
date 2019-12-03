from mypy.plugin import Plugin, ClassDefContext
from mypy.plugins import attrs


def serializable_class_maker_callback(ctx: ClassDefContext):
    return attrs.attr_class_maker_callback(ctx, auto_attribs_default=True)


class CustomPlugin(Plugin):
    def get_class_decorator_hook(self, fullname: str):
        if fullname == "mallennlp.services.serde.serde":
            # Ensures classes decorated with `@serializable` are treated as the
            # the `attr.s` class.
            # TODO: make mypy aware of the methods we add to the class.
            # TODO: make aware that 'slots=True'.
            return serializable_class_maker_callback
        return None


def plugin(version: str):
    return CustomPlugin
