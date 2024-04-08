### Scraper Setup

```python
pip install requirements.txt
```

To run:
```sh
python scraper.py
```

### Front-End Setup

```sh
npm run dev
```

To publish:

```sh
npm run deploy
# Push your changes
git subtree split --branch deploy --prefix epa/dist/
git push https://github.com/davidheineman/epa deploy
```