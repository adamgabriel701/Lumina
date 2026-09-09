from llvmlite import ir

class TypesCodegen:
    def get_llvm_type(self, type_name):
        if type_name == "int": return self.i64_ty
        elif type_name == "float": return self.f64_ty
        elif type_name == "str": return self.voidptr_ty 
        elif type_name == "ptr": return self.i64_ty.as_pointer()
        elif type_name == "bool": return ir.IntType(1)
        elif type_name == "void": return ir.VoidType()
        elif type_name in self.struct_types: return self.struct_types[type_name]
        elif "<" in type_name: return self.get_or_create_monomorphized_struct(type_name)
        return self.i64_ty

    def get_llvm_param_type(self, type_name):
        if type_name in self.struct_types: return self.struct_types[type_name].as_pointer()
        return self.get_llvm_type(type_name)

    def get_llvm_field_type(self, type_name):
        if type_name in self.struct_types: return self.struct_types[type_name].as_pointer()
        return self.get_llvm_type(type_name)

    def get_or_create_monomorphized_struct(self, type_name):
        if type_name in self.struct_types: return self.struct_types[type_name]
        base_name, _, args_str = type_name.partition('<')
        args_str = args_str.rstrip('>')
        type_args = [a.strip() for a in args_str.split(',')]
        if base_name not in self.struct_defs: raise Exception(f"Struct base '{base_name}' não encontrada.")
        base_decl = self.struct_defs[base_name]
        if not base_decl.type_params: raise Exception(f"Struct '{base_name}' não é Genérica.")
        type_map = dict(zip(base_decl.type_params, type_args))
        new_ty = self.module.context.get_identified_type(type_name.replace('<', '_').replace('>', '_').replace(',', '_'))
        self.struct_types[type_name] = new_ty
        field_tys = [self.get_llvm_type(type_map.get(ft, ft)) for ft in base_decl.fields.values()]
        new_ty.set_body(*field_tys)
        self.struct_fields[type_name] = {name: i for i, name in enumerate(base_decl.fields.keys())}
        return new_ty