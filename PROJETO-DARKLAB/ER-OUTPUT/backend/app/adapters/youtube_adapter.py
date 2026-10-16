from typing import List, Dict, Any

class BaseYouTubeAdapter:
    def get_niche_channels(self, tab: str, niche: str = "all") -> List[Dict[str, Any]]:
        raise NotImplementedError

    def analyze_video(self, url_or_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def analyze_channel(self, channel_id: str) -> Dict[str, Any]:
        raise NotImplementedError

class MockYouTubeAdapter(BaseYouTubeAdapter):
    """Adaptador Mock com dados realistas de canais dark, outliers e métricas."""

    SAMPLE_CHANNELS = [
        {
            "channel_id": "UC_ARQUIVOS_PERDIDOS",
            "title": "Arquivos Perdidos",
            "niche": "Mistério & Sobrenatural",
            "subscribers": 14500,
            "views": 260000,
            "age_days": 9,
            "outlier_score": 18.2,
            "is_monetized": True,
            "sparkline": [17.2, 15.3, 12.6, 11.8, 11.3, 9.8, 4.6, 3.0]
        },
        {
            "channel_id": "UC_ECOS_DO_IMPERIO",
            "title": "Ecos do Império",
            "niche": "História Não Contada",
            "subscribers": 28000,
            "views": 310000,
            "age_days": 12,
            "outlier_score": 11.4,
            "is_monetized": True,
            "sparkline": [17.0, 15.8, 15.0, 12.3, 9.7, 6.5, 3.0, 3.0]
        },
        {
            "channel_id": "UC_ABISMO_AZUL",
            "title": "Abismo Azul",
            "niche": "Oceano & Criaturas",
            "subscribers": 9800,
            "views": 140000,
            "age_days": 6,
            "outlier_score": 14.3,
            "is_monetized": False,
            "sparkline": [16.9, 16.4, 14.2, 12.8, 11.3, 9.7, 5.7, 3.0]
        },
        {
            "channel_id": "UC_CIDADES_FANTASMA",
            "title": "Cidades Fantasma",
            "niche": "Lugares Abandonados",
            "subscribers": 35000,
            "views": 320000,
            "age_days": 14,
            "outlier_score": 9.1,
            "is_monetized": True,
            "sparkline": [16.8, 13.7, 10.2, 6.8, 3.3, 3.0, 3.0, 3.0]
        },
        {
            "channel_id": "UC_CRIMES_SILENCIOSOS",
            "title": "Crimes Silenciosos",
            "niche": "True Crime & Perícia",
            "subscribers": 52000,
            "views": 680000,
            "age_days": 21,
            "outlier_score": 13.0,
            "is_monetized": True,
            "sparkline": [18.1, 14.2, 11.0, 8.5, 5.2, 3.1, 2.8, 2.5]
        }
    ]

    def get_niche_channels(self, tab: str, niche: str = "all") -> List[Dict[str, Any]]:
        channels = self.SAMPLE_CHANNELS.copy()
        if tab == "exploding":
            channels.sort(key=lambda x: x["outlier_score"], reverse=True)
        elif tab == "new":
            channels.sort(key=lambda x: x["age_days"])
        elif tab == "rising":
            channels.sort(key=lambda x: x["views"], reverse=True)
        return channels

    def analyze_video(self, url_or_id: str) -> Dict[str, Any]:
        return {
            "video_id": "vid_" + url_or_id[-8:] if len(url_or_id) >= 8 else "vid_sample",
            "title": "O Povoado Que Desapareceu em 1943 Sem Deixar Vestígios",
            "views": 845200,
            "estimated_vph": 1240,
            "retention_score": 88.5,
            "hook_strength": "Alta (Quebra de expectativa no segundo 14)",
            "tags": ["mistério", "desaparecimento", "história sombria", "documentário dark", "relatos reais"],
            "is_monetized": True,
            "summary": "Roteiro em 1ª pessoa estruturado com pergunta polarizadora nos primeiros 20 segundos e revelação fragmentada a cada 2 minutos mantendo a retenção acima de 55%."
        }

    def analyze_channel(self, channel_id: str) -> Dict[str, Any]:
        return {
            "channel_id": channel_id,
            "title": "Arquivos Perdidos",
            "niche": "Mistério & Sobrenatural",
            "subscribers": 14500,
            "video_frequency": "3 vídeos por semana (Seg / Qua / Sex às 19h)",
            "avg_duration_minutes": 16.4,
            "estimated_monthly_revenue": 3840.00,
            "top_outlier_videos": [
                {"title": "Eles Entraram na Caverna Proibida", "views": 420000, "outlier": "x28"},
                {"title": "O Testamento Secreto do Farol", "views": 310000, "outlier": "x21"}
            ]
        }
