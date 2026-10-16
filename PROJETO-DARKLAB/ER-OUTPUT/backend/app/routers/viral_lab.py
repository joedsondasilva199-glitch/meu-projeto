from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any
from backend.app.schemas import NicheChannelItem, VideoAnalysisRequest, VideoAnalysisResponse, ChannelAnalysisResponse
from backend.app.adapters.youtube_adapter import MockYouTubeAdapter
from backend.app.auth import get_current_user
from backend.app.models import User

router = APIRouter(prefix="/api/viral-lab", tags=["Viral Lab (Descobrir)"])
yt_adapter = MockYouTubeAdapter()

@router.get("/niche-finder", response_model=List[NicheChannelItem])
async def get_niche_finder(
    tab: str = Query("exploding", description="exploding, rising, new"),
    niche: str = Query("all"),
    current_user: User = Depends(get_current_user)
):
    channels = yt_adapter.get_niche_channels(tab=tab, niche=niche)
    return [
        NicheChannelItem(
            channel_id=ch["channel_id"],
            title=ch["title"],
            niche=ch["niche"],
            subscribers=ch["subscribers"],
            views=ch["views"],
            age_days=ch["age_days"],
            outlier_score=ch["outlier_score"],
            is_monetized=ch["is_monetized"],
            sparkline=ch.get("sparkline", [])
        )
        for ch in channels
    ]

@router.post("/analyze-video", response_model=VideoAnalysisResponse)
async def analyze_video(req: VideoAnalysisRequest, current_user: User = Depends(get_current_user)):
    data = yt_adapter.analyze_video(req.url_or_id)
    return VideoAnalysisResponse(**data)

@router.post("/analyze-channel", response_model=ChannelAnalysisResponse)
async def analyze_channel(channel_id: str = Query(...), current_user: User = Depends(get_current_user)):
    data = yt_adapter.analyze_channel(channel_id)
    return ChannelAnalysisResponse(**data)

@router.get("/niche-expansion")
async def get_niche_expansion(seed_niche: str = Query("misterio"), current_user: User = Depends(get_current_user)):
    # Grafo de correlação de nichos para expansão e arbitragem
    return {
        "seed_niche": seed_niche,
        "correlated_niches": [
            {"niche": "História Não Contada", "affinity": "92%", "cpm_estimate": "$8.40"},
            {"niche": "Lugares Abandonados", "affinity": "86%", "cpm_estimate": "$7.10"},
            {"niche": "Oceano Profundo & Criaturas", "affinity": "79%", "cpm_estimate": "$6.80"}
        ]
    }
