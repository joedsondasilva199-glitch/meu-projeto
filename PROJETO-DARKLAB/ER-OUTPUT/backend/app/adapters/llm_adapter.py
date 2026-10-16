from typing import Dict, Any

class BaseLLMAdapter:
    def generate_retention_script(self, title: str, niche: str, topic: str, formula_style: str) -> Dict[str, str]:
        raise NotImplementedError

class MockLLMAdapter(BaseLLMAdapter):
    """Adaptador de Roteirização de Alta Retenção baseado nas regras POV e ganchos de 30s."""

    def generate_retention_script(self, title: str, niche: str, topic: str, formula_style: str) -> Dict[str, str]:
        hook = (
            f"Eu nunca imaginei que uma simples decisão mudaria minha vida para sempre. "
            f"Quando olhei para aquele envelope lacrado sobre a mesa, todos riram e me mandaram embora. "
            f"Mas o que eles não sabiam é que aquele segredo estava prestes a custar muito caro."
        )

        open_loop = (
            f"Se você acha que conhece toda a verdade sobre {topic}, espere até ouvir o que a polícia encontrou "
            f"às 3 horas da manhã atrás da parede falsa. Mas para você entender como cheguei até aqui, "
            f"preciso voltar exatamente 48 horas no tempo."
        )

        body = (
            f"Tudo começou de forma comum. Eu trabalhava quieto, observando cada detalhe que passava despercebido. "
            f"No nicho de {niche}, as pessoas costumam ignorar os sinais mais óbvios. "
            f"Enquanto todos prestavam atenção no barulho, eu segui o rastro de poeira até o sótão. "
            f"Ali, escondido sob tábuas antigas, havia um diário encapado em couro desgastado. "
            f"A primeira página trazia um aviso direto: 'Se você está lendo isso, não confie em ninguém da família'."
        )

        cta = (
            f"Se você tivesse encontrado aquele diário, você teria aberto ou deixado trancado? "
            f"Deixe sua resposta nos comentários abaixo. "
            f"E se você quer a parte 2 com o áudio original recuperado, inscreva-se no canal agora."
        )

        full = f"{hook}\n\n{open_loop}\n\n{body}\n\n{cta}"

        return {
            "hook_text": hook,
            "open_loop": open_loop,
            "body_text": body,
            "cta_text": cta,
            "full_script": full
        }
