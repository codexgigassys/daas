# Specifications
## Document objective
This document objective is to explain file and url uploading. "File uploading" refers to uploading a file to be decompiled, while "url uploading" refers to sending a url to download the file.
Is important to note that both features are available through the API, but only file uploading is allowed at the moment using the web page.
We choose to explain how the system resolve those use cases because they are the core of DaaS and, at the same time, they are complex and involve lot of different parts of the system.
## Document audience
The audience are software developers modifying DaaS and operations teams needing help to figure out where a problem may be based on the system's behaviour.

## Content
### URL Upload
![url_upload](/documentation/url_upload.jpg?raw=true)
1. An external system send a URL to the upload endpoint, with an optional callback to inform the external system when the decompilation is done.
2. The URL and the callback go to the metadata queue.
3. The metadata extractor takes a task from the metadata queue, downloads the file and saves it to the distributed file system Seaweedfs.
4. Then the metadata extractor receives an new internal URL from Seaweedfs and sends that url with the metadata and the callback to the sample creation endpoint.
5. The sample creation endpoint creates a new sample, associates the callback with the id of that sample and sends the Seaweed file url to the corresponding queue based on the file type determined by the metadata extractor.
6. A decompiler takes the task from the queue, reads the file from Seaweed, decompiles it, compress the source code and save the compressed file at Seaweed.
7. The decompiler inform the result setting endpoint that the decompilation has been finished.
8. The result of the decompilation is saved and the callback saved at steep 5 is triggered to inform the external system that the decompilation is finished.
9. The external system receives the callback with a URL to download the decompiled result from seaweed.

### File Upload
![file_upload](/documentation/file_upload.jpg?raw=true)
1. An external system send a file to the upload endpoint, with an optional callback to inform the external system when the decompilation is done.
2. THe API saves the file into the distributed file system Seaweedfs.
3. The URL of the saved file and the callback go to the metadata queue.
4. The metadata extractor takes a task from the metadata queue and retrieves the file from Seaweedfs.
5. From now on, follow steeps 4 to 9 of "URL Upload" specification.
