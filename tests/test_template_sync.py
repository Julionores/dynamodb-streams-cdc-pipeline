"""Empêche la dérive entre le code Lambda déployé (inline dans le template
CloudFormation) et sa copie autonome dans src/handler.py, utilisée pour les
tests unitaires. Les deux doivent rester identiques mot pour mot."""

from pathlib import Path

import yaml

TEMPLATE_PATH = Path(__file__).parent.parent / "cloudformation" / "template.yaml"
HANDLER_PATH = Path(__file__).parent.parent / "src" / "handler.py"


def test_inline_lambda_code_matches_standalone_handler_file():
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        # Les fonctions intrinsèques CloudFormation (!Ref, !Sub, !GetAtt...) ne
        # sont pas du YAML standard : on les neutralise pour pouvoir parser le
        # document sans dépendance à un loader CloudFormation dédié.
        content = f.read()

    template = yaml.safe_load(_strip_cfn_tags(content))
    inline_code = template["Resources"]["DynamoDBStreamProcessor"]["Properties"][
        "Code"
    ]["ZipFile"]

    with open(HANDLER_PATH, encoding="utf-8") as f:
        standalone_code = f.read()

    assert inline_code.strip() == standalone_code.strip(), (
        "Le code Lambda inline du template CloudFormation a divergé de "
        "src/handler.py -- mettez les deux à jour ensemble."
    )


def _strip_cfn_tags(content: str) -> str:
    """Remplace les tags courts CloudFormation (!Ref, !GetAtt, !Sub...) par des
    chaînes neutres, uniquement pour permettre un chargement YAML générique."""
    import re

    return re.sub(r"!\w+", "", content)
