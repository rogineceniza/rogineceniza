# Rainy GitHub profile — setup

A cozy, gloomy GitHub profile with a real animated GIF banner, a personal README, an original coding meme, and an automatically regenerated isometric contribution calendar. **Pac-Man and snake are not included.**

## Upload

1. Open `https://github.com/rogineceniza/rogineceniza` (create a **public** repository called `rogineceniza` if needed).
2. Copy `README.md`, the `assets/` folder and `.github/workflows/city.yml` into the repository. **Keep the directories intact**.
3. Remove any previous Pac-Man workflow, `rain-snake.yml`, and outdated Pac-Man/snake README markup.
4. Check **Settings → Actions → General → Workflow permissions**. Allow **Read and write permissions** if needed for your action to commit the SVG. The workflow also requests `contents: write`.
5. Go to **Actions → Rainy Isometric City → Run workflow**. This generates `assets/rainy-city.svg`, which is absent until the first successful run.
6. Check the action logs if your contribution calendar is not yet visible. GitHub's generated SVG may take a short time to render after it commits.

## What is animated?

- `assets/rainy-desk.gif`: 24-frame looping GIF, with moving raindrops, coffee steam, and a blinking cursor. Works on GitHub without any JavaScript, external image host, or workflow.
- The isometric city is a generated static SVG that updates daily, **not** a frame-by-frame animated image.

## Personalize

Edit the intro in `README.md`, focus areas, and developer memes freely. All images are repository-local except third-party stats, badges, and skills icons. If third-party image services are down, only those sections may not load.

The GIF has limited color depth for manageable file size. GitHub may pause GIF playback for viewers who enable reduced motion preferences.
