---
name: open-higgsfield
description: Run, configure and extend OpenHiggsfield, a self-hosted Next.js 16 studio that generates images and videos from one prompt bar through a generation platform API. Use when the user wants to set up or run the studio, configure its environment and platform key, add a model to its catalog or change a model's settings and media inputs, write prompts for its image or video models, or debug a failed or stuck generation.
---

# OpenHiggsfield

A Next.js 16 App Router studio (React 19, Zustand, plain CSS, pnpm). Every generation is one object, `{ model, prompt, media, settings }`. Server actions are the only code that calls the generation API, so the browser never sees the platform key.

## Run it

```bash
pnpm install
pnpm dev          # http://localhost:3000
```

Environment variables, server side only, in `.env.local`:

```
HF_API_BASE_URL=                      # generation API origin
OPEN_HIGGSFIELD_READ_WRITE_TOKEN=     # Vercel Blob read-write token, for uploads
```

In the studio, press **Add key** and paste the platform key as `id:secret`. It's stored in an httpOnly cookie. Never print the key, commit it, or put it in client code.

Other commands: `pnpm build`, `pnpm start`, `pnpm brand` (rebuilds icons and the OG card).

## Where things live

| Path | Purpose |
|---|---|
| `src/generation/catalog/` | One file per model family; `index.ts` lists them in `MODELS` |
| `src/generation/catalog/defaults.ts` | `imageModel()`, `videoModel()` and `t2v()` helpers |
| `src/generation/catalog/types.ts` | `ModelEntry`, `SettingField`, `MediaRole`, `PlatformPaths` |
| `src/generation/actions.ts` | Server actions: key cookie, submit, status |
| `src/generation/platform.ts` | API client: submit is `POST /{model}`, status is `GET /requests/{id}/status`, auth is `Authorization: Key <api_key>` |
| `src/generation/to-platform.ts` | Maps the studio object to the API's own fields |
| `src/openhiggsfield/` | The studio UI: composer, gallery, viewer, pickers |
| `src/app/api/blob` | Issues upload tokens for Vercel Blob |

## Add a model

The catalog is the source of truth: a new entry appears in the model picker with its own settings and media inputs, and no UI changes are needed.

1. Create `src/generation/catalog/<model>.ts`. For a standard model use the helpers:

   ```ts
   import { imageModel, t2v, videoModel } from "./defaults";

   export const myImage = imageModel("my-image", "My Image", { text: "vendor/my-image" });
   export const myVideo = videoModel("my-video", "My Video", { start: 1 }, t2v("vendor/my-video/text-to-video"));
   ```

   `t2v()` derives the matching `image-to-video` path from a `text-to-video` path.
2. For non-standard settings, write the full `ModelEntry`:
   - `surface`: `"image"` or `"video"`.
   - `roles`: the maximum number of inputs per role (`start`, `end`, `reference`, `video`, `audio`).
   - `settings`: fields of type `enum` (`values`, `default`), `range` (`min`, `max`, `default`, optional `step`) or `boolean`.
   - `paths`: `text`, `image`, `firstLast` or `reference` submit paths.
3. Import it in `catalog/index.ts` and add it to `MODELS` where it should appear in the picker.
4. If the API needs field names the shared mapper doesn't produce, add a custom mapping in `to-platform.ts`, as Soul, Kling 3 and Seedance already have.
5. Run `pnpm build` to type-check, then generate once with the new model to confirm it works.

Use only real API paths and settings from the platform's documentation. Never guess model paths.

## Prompts

- Image: subject, composition, style, lighting, colours, aspect ratio, and any exact text in quotes.
- Video: one shot per prompt, the camera move, the subject's action over time, and pacing. With a start frame, describe the motion, not the picture.

## Debug a generation

- **Missing key:** the studio opens the key modal. A missing `HF_API_BASE_URL` throws "Missing HF_API_BASE_URL".
- **Status:** results are polled every 4 seconds until a final status, with a 10-minute deadline. A failed, NSFW or cancelled run shows as a failed tile with the reason and a retry.
- **Uploads:** `blob:` URLs are preview-only. Media must upload to Vercel Blob first, which needs `OPEN_HIGGSFIELD_READ_WRITE_TOKEN`.
- **Old gallery items missing media:** result URLs belong to the platform's CDN and can expire. History is stored in the browser's IndexedDB, capped at 60 records; favourites never age out.
