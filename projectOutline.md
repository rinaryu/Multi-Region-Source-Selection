Packaging (packaging/): This section is responsible for preparing the video files before they are streamed.


transcode.py: This script uses FFmpeg to take a source video and encode it into multiple different bitrates and resolutions so the stream can adapt to different internet speeds.


package.py: This chunks the transcoded video into small segments and creates the initial Media Presentation Description (MPD) manifest file. It notes you might use external tools like Bento4 or Shaka packager for this.


stream_template.py: Provides a base MPD template that the controller will later dynamically modify to inject specific server URLs.


DASH Manifest (dash/): Contains the stream.mpd file. This is the manifest file at the edge of the access network that your source selector will interact with and modify.


Origin Servers (origins/): These are the actual web servers that will host and deliver the video segments to the user.


origin_server.py: A Python script designed to serve the static DASH files while logging request timings and statistics.


nginx.conf: Configuration for Nginx to ensure the servers handle static file serving efficiently and manage cache headers.


The Controller (controller/): This is the "brain" of your project where the source selection logic lives.


controller_api.py: A web service (built with Flask or FastAPI) that handles incoming client requests, receives telemetry data, and returns either a redirect or a customized MPD file.


manifest_rewriter.py: This script takes the stream_template.py and generates a customized, per-session MPD where the video segment URLs are rewritten to point to the server chosen by your policy.


selection_policy.py: The core policy engine that executes the logic to determine which origin server is the "best" or "closest" for the client.


Note on redirector.py: You have this marked with "(delete?)", which implies you are debating whether to handle routing via standard HTTP 302/307 redirects or purely through rewriting the MPD manifest.


Client-Side (client/): The frontend setup used for visual testing and performance tracking.


index.html: The basic user interface for the video player.


dashjs_adapter.js: This script initializes the DASH player and captures crucial performance metrics (like playback starts, buffer emptying, quality changes, and HTTP timings) to feed back to the controller.


Infrastructure as Code (infra/): This directory manages the automated setup of your cloud environments using Terraform.

It contains Terraform modules (like origin/main.tf and multi-region/main.tf) to define and provision the virtual machines across different cloud regions.

Scripts like vm_setup.sh, deploy.py, and deploy.sh act as helpers to automatically configure the VMs (cloud-init), deploy the code, and register the packages.


Testing and Execution (tests/, scripts/): Includes tools for the pipeline, such as validate_mpd.py to ensure the generated manifest files are valid, and pipeline.py to execute the main workflow.