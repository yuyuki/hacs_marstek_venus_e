# How to Add Your Icon to HACS Community Store

## Current Status
✅ Logo files added to repository:
- `logo.png` (root)
- `icon.png` (root)  
- `icon@2x.png` (root)
- `logo@2x.png` (root)
- `custom_components/hacs_marstek_venus_e/icon.png` (integration directory)

✅ Files committed and pushed to GitHub

## To Display Icon in HACS Community Store

HACS displays integration icons from the **Home Assistant Brands** repository. To add your icon:

### Option 1: Submit to Home Assistant Brands (Recommended for Official Display)

1. Fork the Home Assistant Brands repository:
   https://github.com/home-assistant/brands

2. Create a new folder:
   ```
   brands/custom_integrations/hacs_marstek_venus_e/
   ```

3. Add these files to that folder:
   - `icon.png` (256x256px or 512x512px, square)
   - `icon@2x.png` (512x512px or 1024x1024px, square)
   - `logo.png` (can be rectangular)
   - `logo@2x.png` (retina version)

4. Create `manifest.json` in that folder:
   ```json
   {
     "domain": "hacs_marstek_venus_e",
     "name": "Marstek Venus E",
     "integrations": ["hacs_marstek_venus_e"]
   }
   ```

5. Submit a Pull Request to the brands repository

### Option 2: Temporary - Use Direct URL in HACS (For Testing)

While waiting for brands PR approval, users can see your logo in:
- Your GitHub repository README ✅ (working now)
- Integration settings page in Home Assistant
- HACS integration details page

The logo is already accessible at:
```
https://raw.githubusercontent.com/yuyuki/hacs_marstek_venus_e/main/logo.png
```

### Option 3: Let HACS Use Default Icon

HACS will show a default icon until your brand is added to the official repository. The integration will still work perfectly - the icon is just cosmetic for the HACS store listing.

## Where Your Logo Already Appears

✅ **GitHub README** - Shows at the top of your project
✅ **Integration Config** - Shows in Home Assistant when configuring
✅ **Device Page** - Shows on the device details page
✅ **HACS Details** - Shows when viewing your integration in HACS

## What Users See Without Brands PR

Without submitting to the brands repository, users will see:
- Your logo in the README (when browsing GitHub)
- Your logo in HA integration settings
- A default/placeholder icon in the HACS Community Store list

## Recommended Image Sizes

For best results when submitting to brands repository:
- **icon.png**: 256x256px (minimum) or 512x512px (recommended)
- **icon@2x.png**: 512x512px (minimum) or 1024x1024px (recommended)  
- **logo.png**: 256x256px minimum (can be rectangular)
- **logo@2x.png**: 512x512px minimum (can be rectangular)

All should be PNG format with transparency where appropriate.

## Current Logo Info

Your current logo:
- Size: 138,855 bytes
- Format: PNG
- Source: Marstek official product image

This logo is already working in your repository and README. The HACS store icon will show once you submit to the brands repository or after users install your integration.
