# Automated Property Listing Video Generator

An automated video production pipeline for Thai real estate listings.

## Problem
Real estate agents need video content for TikTok and property portals but lack production resources. Manual video creation is time-intensive and inconsistent.

## Solution
A Python pipeline that ingests property data from Google Drive, generates Thai-language voiceover via Gemini TTS, and assembles slide-format videos with synchronized audio. Intended for generative AI videos with dolly-panning shots, but completed using zooming-in shots with FFmpeg in Python due to cost.

## Technical Stack
- Python
- Google Drive API
- Gemini TTS API
- Cron

## Architecture
[ingest → process → video assembly → TTS generation → output]
- Input instructions and images in Google Drive
- Python downloads and processes the images into a video
- Request sent to Google TTS API to process speech
- Video added to audio and temp files deleted
- Python sends video to output folder

## Status
Core pipeline functional. AI video generation layer descoped pending cost optimization. Not currently used in production for listings.

## Future Work
- Integrate AI video generation (Veo, Kling, Runway, Pika, or similar) when cost-per-video becomes viable
- Automate script writing
- Add template system for different property types
- Ready posting for TikTok pending quality check (write captions, hashtags, etc.)
- Complete the front end, replacing Google Drive
