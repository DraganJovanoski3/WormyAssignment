# Media Folder

Place your screenshots and videos here for the PDF documentation.

## Recommended Structure

- `screenshots/` - Screenshot images (.png, .jpg)
- `videos/` - Video files (.mp4, .mov)

## GitHub Video Upload Notes

GitHub supports video files, but:
- **Recommended max size**: 100MB per file
- **Hard limit**: 100MB without Git LFS, 2GB with Git LFS
- **Best practice**: Keep videos under 50MB for better performance

### Options for Large Videos:

1. **Use GitHub Releases**: Upload videos as release assets (up to 2GB)
2. **Compress videos**: Use tools like HandBrake to reduce file size
3. **Use external hosting**: Upload to YouTube/Vimeo and link in your PDF
4. **Use Git LFS**: For files over 100MB (requires Git LFS setup)

### Video Compression Tips:

- Use MP4 format (H.264 codec)
- Reduce resolution (720p is usually enough)
- Lower frame rate if needed
- Use tools like HandBrake or FFmpeg

