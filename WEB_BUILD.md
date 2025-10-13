# Web Dashboard Build Process

This project includes a build step to create a static web dashboard that can be hosted on Netlify or any static hosting service.

## How it Works

The `build_web_dashboard.py` script:

1. **Reads all results data** from the `results/` directory
2. **Embeds the data** directly into the HTML as JavaScript
3. **Creates a static version** of the dashboard that works without a server
4. **Outputs to `dist/index.html`** - a single file that can be opened in any browser

## Building the Dashboard

```bash
python build_web_dashboard.py
```

This creates:
- `dist/index.html` - The complete static dashboard
- All results data embedded as JavaScript
- No server required - just open the HTML file!

## Deployment Options

### Netlify (Recommended)
1. Push your repo to GitHub
2. Connect to Netlify
3. Set build command: `python build_web_dashboard.py`
4. Set publish directory: `dist`
5. Deploy!

### Manual Deployment
1. Run the build script
2. Upload `dist/index.html` to any web server
3. Done!

## Local Development

- **Dynamic dashboard**: Use `python dashboard/server.py` for local development
- **Static dashboard**: Run build script and open `dist/index.html`

## Key Features

- ✅ **No dependencies**: Just HTML, CSS, and JavaScript
- ✅ **Self-contained**: All data embedded in the HTML file
- ✅ **Fast loading**: No API calls needed
- ✅ **Easy hosting**: Works on any static hosting service
- ✅ **Auto-updating**: Rebuild when you have new results

## Notes

- The `dist/` folder is gitignored - it's generated content
- The build script preserves all existing functionality
- Charts, sorting, and filtering all work in the static version
- No changes to your existing dashboard code
