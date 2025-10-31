#!/usr/bin/env python3
"""
🧠 NEURAL CODE MUTATOR
======================
KI-gesteuerte Code-Mutation um Signaturen zu umgehen
"""
import ast
import hashlib
import random


class NeuralCodeMutator:

    def __init__(self):
        self.obfuscation_techniques = [
            self.variable_name_mutation,
            self.control_flow_obfuscation,
            self.string_encryption,
            self.dead_code_injection,
            self.function_splitting,
        ]

    def variable_name_mutation(self, code):
        """Mutiert Variablennamen zu kryptischen Bezeichnern"""
        tree = ast.parse(code)

        # Sammle alle Variablennamen
        var_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                var_names.add(node.id)

        # Erstelle Mutations-Mapping mit kryptischen Namen
        mutation_map = {}
        for var_name in var_names:
            if not var_name.startswith('__'):  # Schütze Magic-Methods
                # Generiere kryptischen Namen basierend auf Hash
                hash_input = var_name + "neural_mutation_2024"
                hash_obj = hashlib.md5(hash_input.encode())
                hex_hash = hash_obj.hexdigest()[:8]
                mutation_map[var_name] = f"_{hex_hash}_"

        # Wende Mutationen an
        class VariableMutator(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id in mutation_map:
                    node.id = mutation_map[node.id]
                return node

        mutator = VariableMutator()
        mutated_tree = mutator.visit(tree)

        import astor
        return astor.to_source(mutated_tree)

    def control_flow_obfuscation(self, code):
        """Verschleiert Control Flow mit opaque predicates"""
        tree = ast.parse(code)

        class FlowObfuscator(ast.NodeTransformer):
            def visit_If(self, node):
                # Erstelle opaque predicate (immer True, aber schwer zu erkennen)
                # Beispiel: (x*x + x) % 2 == x % 2 (immer True für jede ganze
                # Zahl x)
                x_var = ast.Name(id='__neural_x__', ctx=ast.Load())
                opaque_pred = ast.Compare(
                    left=ast.BinOp(
                        left=ast.BinOp(
                            left=ast.BinOp(
                                left=x_var,
                                op=ast.Mult(),
                                right=x_var),
                            op=ast.Add(),
                            right=x_var),
                        op=ast.Mod(),
                        right=ast.Num(
                            n=2)),
                    ops=[
                        ast.Eq()],
                    comparators=[
                        ast.BinOp(
                            left=x_var,
                            op=ast.Mod(),
                            right=ast.Num(
                                n=2))])

                # Kombiniere mit originaler Bedingung
                if isinstance(node.test,
                              ast.NameConstant) and node.test.value is True:
                    node.test = opaque_pred
                else:
                    node.test = ast.BoolOp(
                        op=ast.And(),
                        values=[opaque_pred, node.test]
                    )

                return self.generic_visit(node)

        obfuscator = FlowObfuscator()
        obfuscated_tree = obfuscator.visit(tree)

        # Füge __neural_x__ Variable hinzu
        init_stmt = ast.Assign(
            targets=[ast.Name(id='__neural_x__', ctx=ast.Store())],
            value=ast.Num(n=random.randint(1, 1000))
        )
        obfuscated_tree.body.insert(0, init_stmt)

        import astor
        return astor.to_source(obfuscated_tree)

    def string_encryption(self, code):
        """Verschlüsselt String-Literale mit XOR-Cipher"""
        tree = ast.parse(code)

        def xor_encrypt(text, key):
            return ''.join(chr(ord(c) ^ key) for c in text)

        encryption_key = random.randint(1, 255)

        class StringEncryptor(ast.NodeTransformer):
            def visit_Str(self, node):
                if len(node.s) > 3:  # Nur längere Strings verschlüsseln
                    encrypted = xor_encrypt(node.s, encryption_key)
                    encrypted_bytes = [ord(c) for c in encrypted]

                    # Erstelle Decryption-Call
                    decrypt_call = ast.Call(
                        func=ast.Name(
                            id='__neural_decrypt__', ctx=ast.Load()), args=[
                            ast.List(
                                elts=[
                                    ast.Num(
                                        n=b) for b in encrypted_bytes], ctx=ast.Load()), ast.Num(
                                n=encryption_key)], keywords=[])
                    return decrypt_call
                return node

        encryptor = StringEncryptor()
        encrypted_tree = encryptor.visit(tree)

        # Füge Decryption-Funktion hinzu
        decrypt_func = """
def __neural_decrypt__(encrypted_bytes, key):
    return ''.join(chr(b ^ key) for b in encrypted_bytes)
"""

        import astor
        encrypted_code = astor.to_source(encrypted_tree)
        return decrypt_func + "\n" + encrypted_code

    def dead_code_injection(self, code):
        """Injiziert toten Code zur Signatur-Verschleierung"""
        tree = ast.parse(code)

        # Generiere realistischen aber nutzlosen Code
        dead_code_snippets = [
            f"__neural_var_{
                random.randint(
                    1000, 9999)} = {
                random.randint(
                    1, 100)} * {
                        random.randint(
                            1, 100)}", f"__neural_list_{
                                random.randint(
                                    1000, 9999)} = [i for i in range({
                                        random.randint(
                                            5, 20)})]", f"__neural_dict_{
                                                random.randint(
                                                    1000, 9999)} = {
                                                        'key_{i}': {
                                                            random.randint(
                                                                1, 100)} for i in range({
                                                                    random.randint(
                                                                        3, 8)})} ", ]

        class DeadCodeInjector(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                # Füge toten Code am Anfang der Funktion hinzu
                dead_stmt = ast.parse(
                    random.choice(dead_code_snippets)).body[0]
                node.body.insert(0, dead_stmt)

                return self.generic_visit(node)

        injector = DeadCodeInjector()
        injected_tree = injector.visit(tree)

        import astor
        return astor.to_source(injected_tree)

    def function_splitting(self, code):
        """Teilt große Funktionen in kleinere auf"""
        tree = ast.parse(code)

        class FunctionSplitter(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if len(node.body) > 5:  # Nur große Funktionen teilen
                    # Teile Funktion in der Mitte
                    mid = len(node.body) // 2

                    # Erstelle Hilfsfunktion
                    helper_name = f"__neural_helper_{
                        random.randint(
                            1000, 9999)}__"
                    helper_func = ast.FunctionDef(
                        name=helper_name,
                        args=node.args,  # Gleiche Parameter
                        body=node.body[mid:],  # Zweite Hälfte
                        decorator_list=[],
                        returns=None
                    )

                    # Erstelle Call zur Hilfsfunktion
                    helper_call = ast.Expr(
                        value=ast.Call(
                            func=ast.Name(
                                id=helper_name,
                                ctx=ast.Load()),
                            args=[
                                ast.Name(
                                    id=arg.arg,
                                    ctx=ast.Load()) for arg in node.args.args],
                            keywords=[]))

                    # Modifiziere ursprüngliche Funktion
                    node.body = node.body[:mid] + [helper_call]

                    # Füge Hilfsfunktion vor ursprünglicher ein
                    return [helper_func, node]

                return self.generic_visit(node)

        splitter = FunctionSplitter()
        split_tree = splitter.visit(tree)

        import astor
        return astor.to_source(split_tree)

    def neural_mutation_pipeline(
            self,
            source_file,
            output_file,
            mutation_intensity=3):
        """Führt komplette neurale Mutation durch"""
        print(f"🧠 NEURAL CODE MUTATION - INTENSITY {mutation_intensity}")
        print("=" * 50)

        with open(source_file) as f:
            original_code = f.read()

        mutated_code = original_code
        applied_mutations = []

        # Wende zufällige Mutationen an
        selected_techniques = random.sample(
            self.obfuscation_techniques, min(
                mutation_intensity, len(
                    self.obfuscation_techniques)))

        for technique in selected_techniques:
            try:
                mutated_code = technique(mutated_code)
                applied_mutations.append(technique.__name__)
                print(f"  ✅ {technique.__name__} angewendet")
            except Exception as e:
                print(f"  ❌ {technique.__name__} fehlgeschlagen: {e}")

        # Signatur-Hash vor und nach Mutation
        original_hash = hashlib.md5(original_code.encode()).hexdigest()[:8]
        mutated_hash = hashlib.md5(mutated_code.encode()).hexdigest()[:8]

        with open(output_file, 'w') as f:
            f.write(mutated_code)

        print("\n🎯 MUTATION COMPLETE:")
        print(f"  📊 Techniken angewendet: {len(applied_mutations)}")
        print(f"  🔐 Original Hash: {original_hash}")
        print(f"  🔐 Mutiert Hash: {mutated_hash}")
        print(f"  📝 Output: {output_file}")

        return output_file, applied_mutations


if __name__ == "__main__":
    mutator = NeuralCodeMutator()
    mutator.neural_mutation_pipeline(
        "target.py",
        "target_mutated.py",
        mutation_intensity=5)
