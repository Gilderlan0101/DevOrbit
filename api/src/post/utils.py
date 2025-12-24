from typing import Any, Dict


class DataProcessing:
    def filter_unsubmitted_or_default_fields(
        self, content: dict
    ) -> Dict[str, Any]:
        """Remove campos não enviados ou com valores padrão não modificados.

        Remove do dicionário:
        1. Campos que não foram enviados no request
        2. Campos enviados apenas com valores padrão não modificados
           (ex: 'value': 'string')

        Args:
            content: Dicionário com dados do schema a ser filtrado

        Returns:
            Dicionário com apenas os campos realmente preenchidos pelo usuário
        """
        import json

        updated_fields = {}
        if content:

            for field, value in content.items():
                if isinstance(value, dict):
                    value = json.dumps(value, ensure_ascii=False)

                if value in [None, 'string', ' ']:
                    continue
                if isinstance(value, (int, float)) and value == 0:
                    continue

                if field == 'photo' or field == 'imagem_path' and value:
                    value = str(value)

                if value not in ['', ' ', 'string', None]:
                    updated_fields[field] = value

        if not content:
            return {'message': 'Nenhum campo relevante para atualizar.'}

        return updated_fields
