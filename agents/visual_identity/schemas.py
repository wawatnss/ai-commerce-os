"""Pydantic schemas for the Brand Asset Pack."""

from pydantic import BaseModel, Field
from typing import List


class Color(BaseModel):
    name: str
    hex: str
    usage: str


class Typography(BaseModel):
    heading: str
    body: str
    accent: str
    note: str


class IconSet(BaseModel):
    style: str
    recommended: List[str]


class ImagePrompt(BaseModel):
    name: str
    prompt: str
    negative_prompt: str
    aspect_ratio: str
    style_tags: List[str]


class BrandingPack(BaseModel):
    logo_svg: str = Field(..., description="Inline SVG logo")
    favicon_svg: str = Field(..., description="Inline SVG favicon")
    palette: List[Color]
    icons: IconSet
    typography: Typography


class StoreAssetPrompts(BaseModel):
    hero_banner: ImagePrompt
    category_banner: ImagePrompt
    newsletter_banner: ImagePrompt


class ProductAssetPrompts(BaseModel):
    product_hero: ImagePrompt
    lifestyle: ImagePrompt
    packshot: ImagePrompt
    mockup: ImagePrompt


class MarketingAssetPrompts(BaseModel):
    instagram_post: ImagePrompt
    tiktok_cover: ImagePrompt
    pinterest: ImagePrompt
    facebook_cover: ImagePrompt
    email_header: ImagePrompt


class BrandAssetPack(BaseModel):
    branding: BrandingPack
    store: StoreAssetPrompts
    product: ProductAssetPrompts
    marketing: MarketingAssetPrompts
    source_palette: str = Field(..., description="How the palette was derived")
