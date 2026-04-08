# Multi-Region-Source-Selection
A smaller scale Dynamic Adaptive Streaming over HTTP (DASH) application which deploys web servers from several different geographic locations. The proxy that routes within the distributed content delivery network does so based on server proximity and geographic distance.


## Used/Required Packages
ffmpeg: Creating specific bitrate rendition(s) for content.
Bento4 v1.6.0.640 (or higher): Used to segment media content and build initial manifest for corresponding segments.
Flask: The controller framework that receives user requests and runs the source selector.
