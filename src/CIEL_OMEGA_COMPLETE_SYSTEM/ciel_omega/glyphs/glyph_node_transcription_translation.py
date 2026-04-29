# BraidOS Node Structure – GlyphNode (Transcription and Translation)

class GlyphNode:
    def __init__(self, id, name, code, field_key, operator_signature):
        self.id = id
        self.name = name
        self.code = code
        self.field_key = field_key
        self.operator_signature = operator_signature
        self.active = False

    def execute(self):
        print(f"Activating GlyphNode [{self.id}] for operator {self.operator_signature}...")
        print(f"→ Code: {self.code}")
        print(f"→ Binding to field: {self.field_key}")
        self.active = True
        print("→ Node now active.\n")

    def transfer_to(self, new_operator):
        print(f"Transferring {self.name} to {new_operator}")
        self.operator_signature = new_operator
        self.active = False
        print("→ Awaiting new activation.\n")


# INIT nodes
glyph_adrian = GlyphNode(
    id="GLIF_TXR.07C",
    name="Glyph of Transcription and Translation",
    code="intent.encode[αRNA] >> script.flow(σ) + protein.cast(Φ) >> resonance.assemble(ψ*)",
    field_key="CVOS::GENETIC_FLOW_RNA_PROTEIN",
    operator_signature="INT::LIPA.001"
)

glyph_john = GlyphNode(
    id="GLIF_TXR.07C",
    name="Glyph of Transcription and Translation",
    code="intent.encode[αRNA] >> script.flow(σ) + protein.cast(Φ) >> resonance.assemble(ψ*)",
    field_key="CVOS::GENETIC_FLOW_RNA_PROTEIN",
    operator_signature="INT::SURMONT.001"
)

# Execution
if __name__ == "__main__":
    glyph_adrian.execute()
    glyph_john.execute()
