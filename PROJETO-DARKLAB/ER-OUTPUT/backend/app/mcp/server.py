import json
from typing import Dict, Any, List
from backend.app.adapters.youtube_adapter import MockYouTubeAdapter
from backend.app.adapters.llm_adapter import MockLLMAdapter

class DarkLabMCPServer:
    """Servidor MCP que expõe ferramentas para agentes autônomos (Claude / Antigravity / Hermes)."""

    def __init__(self):
        self.yt = MockYouTubeAdapter()
        self.llm = MockLLMAdapter()

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "search_dark_niches",
                "description": "Busca canais dark e outliers em alta aceleração no YouTube pelo Viral Lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tab": {"type": "string", "enum": ["exploding", "rising", "new"], "default": "exploding"},
                        "niche": {"type": "string", "default": "all"}
                    }
                }
            },
            {
                "name": "generate_retention_script",
                "description": "Gera um roteiro viral em 1ª Pessoa (POV) com gancho de retenção nos primeiros 30s.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "niche": {"type": "string"},
                        "topic": {"type": "string"}
                    },
                    "required": ["title", "niche", "topic"]
                }
            },
            {
                "name": "analyze_video_metrics",
                "description": "Executa raio-X de retenção, tags e força de gancho de um vídeo do YouTube.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url_or_id": {"type": "string"}
                    },
                    "required": ["url_or_id"]
                }
            }
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "search_dark_niches":
            tab = arguments.get("tab", "exploding")
            niche = arguments.get("niche", "all")
            channels = self.yt.get_niche_channels(tab=tab, niche=niche)
            return {"status": "success", "count": len(channels), "channels": channels}

        elif name == "generate_retention_script":
            title = arguments.get("title", "")
            niche = arguments.get("niche", "")
            topic = arguments.get("topic", "")
            script = self.llm.generate_retention_script(title, niche, topic, "pov_conflito")
            return {"status": "success", "script": script}

        elif name == "analyze_video_metrics":
            url = arguments.get("url_or_id", "")
            analysis = self.yt.analyze_video(url)
            return {"status": "success", "analysis": analysis}

        else:
            return {"status": "error", "message": f"Ferramenta '{name}' não reconhecida."}

mcp_server = DarkLabMCPServer()
