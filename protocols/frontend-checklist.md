# Frontend Delivery Checklist

**Version:** 1.0  
**Applies to:** Any cycle whose deliverable is HTML, JavaScript, WebGL, Canvas, CSS, or any browser-rendered artifact.

This checklist is **mandatory** for any agent involved in producing, reviewing, or verifying a frontend deliverable. It supplements — not replaces — the agent's standard role-specific output.

---

## When this checklist applies

A deliverable is "frontend" when:
- The output is an HTML file, JS module, or browser page
- The output uses external CDN scripts (Three.js, D3, etc.)
- The output uses Canvas 2D, WebGL, SVG animation, or CSS animation
- The output will be evaluated by a human looking at a browser window

---

## Developer checklist (before marking task COMPLETED)

- [ ] **CDN loading order verified**: every `<script src="...cdn...">` that uses `defer` or `async` must load BEFORE any code that depends on the global it sets (e.g. `window.THREE`). If a CDN script is `defer`-ed, dependent code must be in a `DOMContentLoaded` listener — and the CDN must be known to execute before that event fires.
- [ ] **CDN URL pinned to a known-working path**: unpkg paths may serve ES modules instead of UMD globals depending on the version. Prefer versioned cdnjs paths for globals (e.g. `cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`).
- [ ] **`onerror` on each external `<script>` tag**: silent 404s or module-format mismatches must surface as console errors.
- [ ] **`try/catch` around WebGL/Canvas context creation**: WebGL unavailability must not kill the entire animation loop; use a fallback message.
- [ ] **Graceful fallback when JS fails**: a visible DOM element (not just `return null`) must appear when a dependency fails to load.
- [ ] **Opened in browser and visual output confirmed**: the developer (or a human operator) must open the file in a browser and confirm the animation/rendering works before committing.
- [ ] **Browser console shows no errors**.
- [ ] **Responsive check**: if the page is responsive, confirm the layout does not break at ≤480px width.
- [ ] **`prefers-reduced-motion` respected**: animations must pause or simplify when the OS accessibility setting is active.

---

## Reviewer checklist (additional items for frontend code reviews)

- [ ] **Script tag loading order**: confirm CDN dependencies are loaded before dependent inline code. `defer`/`async` on dependencies creates race conditions — flag any such pattern.
- [ ] **Global namespace pollution**: confirm CDN globals (`window.THREE`, etc.) are used defensively with null checks.
- [ ] **Error surfacing**: confirm failed dependency loads produce a `console.error`, not silent `null` returns.
- [ ] **Canvas/WebGL initialization**: confirm context creation is guarded with `try/catch`.
- [ ] **CDN version pinning**: confirm the CDN URL is a versioned, stable path — not a `latest` or unversioned alias.

---

## Tester smoke test protocol (browser)

**Trigger**: any task whose deliverable includes an HTML file with JS animation/WebGL.

**Steps**:
1. Open the HTML file in a browser (Chrome or Firefox, hardware acceleration enabled)
2. Check DevTools → Network: confirm all `<script>` CDN tags return HTTP 200
3. Check DevTools → Console: confirm zero errors
4. Visual check: confirm the animated element renders (not blank, not white box)
5. If Three.js/WebGL: confirm the canvas contains 3D geometry (spheres, lines, etc.)
6. Wait for any transition animations to fire; confirm they work
7. Resize window to ≤480px: confirm layout does not break

**Pass criteria**: steps 2–7 all pass with no errors.  
**Fail criteria**: any CDN 404, any console error, any blank canvas, any layout breakage.

---

## Scientist verification note

For frontend deliverables, **logical inspection alone does not satisfy Step 9**. The required verification method is **Browser observation**: open the file in a browser and directly observe runtime behavior. Benchmark, simulation, and logical proof are insufficient substitutes for visual rendering verification.

---

## Common failure patterns (learn from these)

| Pattern | Symptom | Fix |
|---------|---------|-----|
| CDN script with `defer` + dependent inline code | Dependency undefined at runtime; silent failure | Remove `defer`, or ensure dependent code is in `DOMContentLoaded` listener and CDN script executes before that event |
| unpkg path for wrong version serving ES module instead of UMD | `window.THREE` undefined | Use cdnjs with explicit `r128/three.min.js` path for Three.js globals |
| `if (!dep) return null` without logging | Silent blank canvas, no developer hint | Replace with `console.error` + visible DOM fallback |
| WebGL constructor without try/catch | Exception kills entire animation loop | Wrap in try/catch, show fallback on catch |
| Canvas width from `clientWidth` before layout | Zero-sized renderer | Read size after `DOMContentLoaded`, add non-zero fallback |
