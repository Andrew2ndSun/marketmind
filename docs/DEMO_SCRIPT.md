# Three-minute demo script

Target: 180 seconds maximum. Show only the new MarketMind workflow. Record the actual
Muse-backed product. Keep keys, System Properties and account/billing screens off video.
A captioned local recording is useful, but a final public video URL must be checked.

| Time | Screen | Narration / caption |
| --- | --- | --- |
| 0:00-0:20 | Market radar and industry themes | A scheduled Muse job reviews broad economic/business news and saves 10 sourced research candidates every two hours. Theme: Build for Your World. |
| 0:20-0:35 | Select a radar stock to fill the form | I adapted an earlier data-fetching foundation. During this event I built the market radar, Muse research integration, structured cited reports, evidence dashboard and validation. The inherited trading code is excluded. |
| 0:35-1:05 | Click Investigate for the selected stock; show real loading | This request collects completed price history, provider fundamentals and available ticker news, then asks Muse Spark to reason over bounded evidence. There is no other model provider or canned response. |
| 1:05-1:30 | Brief and a citation | The report separates observations from hypotheses. Clicking M1 shows the exact numeric evidence and timestamps. Citation IDs are checked; that alone does not prove the claim is true. |
| 1:30-1:50 | Findings and counterpoints | I can inspect what supports the narrative and what challenges it. If news is missing, the report flags that gap rather than inventing a catalyst. |
| 1:50-2:10 | Risk and unknowns | Volatility and drawdown describe the historical window. They are not price forecasts. These unresolved questions show what needs further investigation. |
| 2:10-2:30 | Model/method details and JSON export | Here is the actual Muse model and token usage. I can export the evidence and report together for review. Keys never reach the browser. |
| 2:30-2:50 | Validation/code or tests | The new code rejects malformed JSON, unknown citations and truncated output. Offline tests cover failure paths, fixed Muse routing and numerical behavior. |
| 2:50-3:00 | Product | MarketMind makes stock research easier to inspect. It is educational research, with explicit uncertainty and no trading instructions. |

## Recording checks

- Keep the recording at or under three minutes; confirm duration with a media tool.
- Use a real Muse response. If a live request fails, retry or record later; do not
  replace the response with an invented success screen.
- Do not claim news-based reasoning if the actual run has no news.
- Use captions or narration to identify new contributions in the recording itself.
- Upload the final video through a service you authorize. Test its link signed out.
- Put the public video and repository URLs in the CV submission and list contributors.

A real captioned local recording is available at `artifacts/marketmind-demo.webm` (175.56 seconds). It has no audio narration. Review the entire recording before hosting it. To rerun the recorder on another machine, optionally install Playwright and Chromium (`python -m pip install playwright`, then `python -m playwright install chromium`).

The current local recording predates the market radar and needs re-recording to show the new feature. Do not imply the radar appears in that older footage.

Start the server and allow the first scheduled radar scan to finish before recording. The recorder waits for the saved real radar result and selects its first candidate before explicitly starting full research. It stops if the live calls exceed the allotted recording segments instead of substituting fake results.
