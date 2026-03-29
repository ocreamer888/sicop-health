# @/Users/macm1air/.cursor/projects/Users-macm1air-Documents-C…

Source: `../../../.cursor/projects/Users-macm1air-Documents-Code-sicop-health/agent-transcripts/cfbab4f9-afec-4e1c-a044-63aa335c6993.jsonl`

---

**User**

<attached_files>

<terminal_selection title="Terminal" path="/Users/macm1air/.cursor/projects/Users-macm1air-Documents-Code-sicop-health/terminals/6.txt" lines="284-1014">
(venv) macm1air@Ocreamer-3 etl % python main.py 90 
/Users/macm1air/Documents/Code/sicop-health/services/etl/classifier.py:12: SyntaxWarning: invalid escape sequence '\s'
  3. r"activos?\s+(de\s+)?uso\s+medic" movido a PATRONES_REGEX — ahora usa \s+ que
/Users/macm1air/Documents/Code/sicop-health/services/etl/venv/lib/python3.13/site-packages/requests/__init__.py:113: RequestsDependencyWarning: urllib3 (1.26.20) or chardet (7.0.1)/charset_normalizer (3.4.4) doesn't match a supported version!
  warnings.warn(
2026-03-05 15:30:34,592 [INFO] main — === SICOP ETL — Iniciando (dias_atras=90) ===
2026-03-05 15:30:35,349 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
[fetcher:publicadas] 4512 registros / 46 páginas
2026-03-05 15:30:35,714 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:35,934 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:36,109 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:36,314 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:36,504 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:36,715 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:36,989 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:37,161 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:37,355 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:37,601 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:37,791 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:38,033 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:38,229 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:38,416 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:38,622 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:38,804 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:39,110 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:39,307 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:39,514 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:39,720 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
[fetcher:publicadas] página 20/46
2026-03-05 15:30:39,927 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:40,130 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:40,541 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:40,773 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:40,982 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:41,315 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:41,521 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:41,814 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:42,047 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:42,263 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:42,592 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:42,831 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:43,054 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:43,357 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:43,577 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:43,883 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:44,169 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:44,544 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:44,874 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:45,170 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
[fetcher:publicadas] página 40/46
2026-03-05 15:30:45,418 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:45,663 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:45,897 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:46,127 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
2026-03-05 15:30:46,457 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageRelease "HTTP/1.1 200 OK"
[fetcher:publicadas] 1011 de 4512 son instituciones target
2026-03-05 15:30:52,224 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
[fetcher:adjudicadas] 16539 registros / 166 páginas
2026-03-05 15:30:55,027 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:30:57,953 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:01,177 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:04,074 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:06,914 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:09,843 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:12,862 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:15,879 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:18,399 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:21,101 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:23,760 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:26,875 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:29,846 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:32,670 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:35,528 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:38,294 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:41,711 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:44,708 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:47,666 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:50,687 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
[fetcher:adjudicadas] página 20/166
2026-03-05 15:31:53,780 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:56,591 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:31:59,418 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:02,035 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:04,823 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:07,726 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:10,553 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:16,666 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:19,756 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:22,573 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:26,377 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:29,376 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:32,341 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:35,336 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:38,920 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:41,579 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:44,546 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:47,357 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:49,418 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:52,812 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
[fetcher:adjudicadas] página 40/166
2026-03-05 15:32:54,941 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:32:57,738 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:00,403 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:02,567 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:06,196 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:09,111 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:12,302 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:15,779 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:19,178 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:21,024 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:24,213 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:27,407 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:29,411 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:32,332 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:35,246 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:37,085 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:40,258 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:43,139 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:46,451 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:49,575 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
[fetcher:adjudicadas] página 60/166
2026-03-05 15:33:50,776 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:53,975 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:55,068 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:57,888 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:33:58,837 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:01,664 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:02,783 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:05,777 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:08,702 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:12,399 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:15,878 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:19,330 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:22,155 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:25,579 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:28,508 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:29,536 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:32,515 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:35,413 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:38,511 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:39,644 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
[fetcher:adjudicadas] página 80/166
2026-03-05 15:34:42,618 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:43,742 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:46,806 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:49,940 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:53,061 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:55,815 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:34:58,675 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:01,440 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:04,413 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:07,383 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:10,367 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:11,491 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:14,619 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:17,823 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:20,765 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:23,677 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:24,767 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:27,711 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:30,623 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:33,753 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
[fetcher:adjudicadas] página 100/166
2026-03-05 15:35:36,888 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:39,652 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:43,034 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:46,052 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:47,224 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:50,388 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:53,395 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:56,435 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:35:59,647 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:02,946 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:06,265 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:09,401 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:12,541 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:13,709 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:16,757 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:20,410 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:23,810 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:26,171 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:27,588 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:28,638 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
[fetcher:adjudicadas] página 120/166
2026-03-05 15:36:29,812 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:30,840 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:31,831 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:33,003 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:34,092 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:35,112 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:36,140 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:37,149 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:38,325 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:39,445 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:40,696 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:41,897 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:43,043 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:44,114 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:45,162 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:46,229 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:47,285 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:48,322 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:49,380 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:50,449 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
[fetcher:adjudicadas] página 140/166
2026-03-05 15:36:51,537 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:52,623 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:53,669 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:54,784 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:56,209 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:57,628 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:58,690 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:36:59,843 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:00,906 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:02,032 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:03,067 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:04,122 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:05,273 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:06,422 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:07,512 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:08,760 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:09,968 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:11,260 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:12,817 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:13,951 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
[fetcher:adjudicadas] página 160/166
2026-03-05 15:37:15,133 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:16,226 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:17,371 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:18,754 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
2026-03-05 15:37:19,706 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageAwarded "HTTP/1.1 200 OK"
[fetcher:adjudicadas] 6110 de 16539 son instituciones target
2026-03-05 15:37:23,218 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
[fetcher:modificadas] 11734 registros / 118 páginas
2026-03-05 15:37:26,551 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:37:29,599 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:37:32,540 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:37:35,918 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:37:38,849 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:37:41,689 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:37:44,816 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:37:47,659 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:37:50,928 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:37:54,256 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:37:57,101 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:00,131 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:03,262 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:06,406 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:09,515 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:12,593 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:16,095 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:20,262 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:23,931 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:27,591 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
[fetcher:modificadas] página 20/118
2026-03-05 15:38:30,734 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:33,755 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:37,091 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:41,004 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:44,486 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:48,195 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:51,323 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:54,226 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:38:57,168 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:00,902 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:05,420 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:09,334 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:12,606 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:15,826 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:18,830 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:22,336 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:25,703 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:29,543 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:33,036 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:36,772 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
[fetcher:modificadas] página 40/118
2026-03-05 15:39:40,200 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:43,406 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:46,719 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:49,669 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:52,809 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:56,356 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:39:59,926 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:03,013 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:06,420 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:09,983 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:13,265 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:16,484 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:20,073 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:23,472 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:27,230 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:30,870 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:34,235 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:37,140 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:40,152 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:43,336 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
[fetcher:modificadas] página 60/118
2026-03-05 15:40:46,540 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:50,713 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:53,615 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:40:57,398 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:01,414 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:05,284 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:09,583 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:13,756 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:17,458 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:21,301 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:25,111 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:28,436 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:31,856 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:34,895 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:37,915 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:40,849 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:43,857 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:46,772 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:50,262 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:41:54,198 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
[fetcher:modificadas] página 80/118
2026-03-05 15:41:57,140 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:00,051 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:02,878 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:05,830 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:08,807 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:12,163 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:15,674 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:18,658 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:21,754 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:25,199 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:28,320 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:31,209 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:34,120 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:37,063 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:40,079 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:43,486 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:46,604 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:49,806 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:52,874 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:42:55,791 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
[fetcher:modificadas] página 100/118
2026-03-05 15:42:58,673 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:01,876 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:05,066 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:08,079 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:11,107 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:14,224 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:17,024 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:20,391 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:23,322 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:26,449 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:29,269 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:32,246 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:35,247 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:38,323 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:41,604 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:44,527 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
2026-03-05 15:43:47,520 [INFO] httpx — HTTP Request: POST https://prod-api.sicop.go.cr/bid/api/v1/public/epCartelReleaseAdjuMod/listPageModified "HTTP/1.1 200 OK"
[fetcher:modificadas] 4967 de 11800 son instituciones target
[fetcher] ✓ 1011 pub | 973 adj | 392 mod
2026-03-05 15:43:47,763 [INFO] parser — [parser] 1011 items parseados — type_key: RPT_PUB
  SIN_CATEGORIA: 'preparacion antihemorroidal unguento tubo con 30 g a 60 g, codigo: 1-10-49-2450 '
  SIN_CATEGORIA: 'betametasona 0.1. unguento. tubo con 15 g. cod: insti: 1-10-46-2470'
2026-03-05 15:43:49,608 [INFO] httpx — HTTP Request: POST https://ofjsiatheyuhhdpxfaea.supabase.co/rest/v1/licitaciones_medicas?on_conflict=numero_procedimiento&columns=%22fecha_tramite%22%2C%22estado%22%2C%22institucion%22%2C%22descripcion%22%2C%22raw_data%22%2C%22tipo_procedimiento%22%2C%22categoria%22%2C%22numero_procedimiento%22%2C%22es_medica%22 "HTTP/2 201 Created"
2026-03-05 15:43:49,955 [INFO] uploader — [uploader] 1011 licitaciones upserted
[uploader] 1011 licitaciones upserted
2026-03-05 15:43:49,955 [INFO] main — [publicadas] 271 médicas de 1011 totales (27%)
2026-03-05 15:43:49,962 [INFO] parser — [parser] 973 items parseados — type_key: RPT_ADJ
2026-03-05 15:43:50,794 [INFO] httpx — HTTP Request: POST https://ofjsiatheyuhhdpxfaea.supabase.co/rest/v1/licitaciones_medicas?on_conflict=numero_procedimiento&columns=%22currency_type%22%2C%22fecha_tramite%22%2C%22estado%22%2C%22institucion%22%2C%22descripcion%22%2C%22cartel_cate%22%2C%22tipo_procedimiento%22%2C%22raw_data%22%2C%22categoria%22%2C%22monto_colones%22%2C%22numero_procedimiento%22%2C%22es_medica%22 "HTTP/2 400 Bad Request"
Traceback (most recent call last):
  File "/Users/macm1air/Documents/Code/sicop-health/services/etl/main.py", line 125, in <module>
    asyncio.run(run(dias_atras=dias))
    ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/base_events.py", line 725, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "/Users/macm1air/Documents/Code/sicop-health/services/etl/main.py", line 77, in run
    upsert_licitaciones(clasificados)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/Users/macm1air/Documents/Code/sicop-health/services/etl/uploader.py", line 126, in upsert_licitaciones
    .execute()
     ~~~~~~~^^
  File "/Users/macm1air/Documents/Code/sicop-health/services/etl/venv/lib/python3.13/site-packages/postgrest/_sync/request_builder.py", line 53, in execute
    raise APIError(dict(json_obj))
postgrest.exceptions.APIError: {'message': "Could not find the 'currency_type' column of 'licitaciones_medicas' in the schema cache", 'code': 'PGRST204', 'hint': None, 'details': None}
</terminal_selection>

</attached_files>
<user_query>
@/Users/macm1air/.cursor/projects/Users-macm1air-Documents-Code-sicop-health/terminals/6.txt:284-1014 

Analyze and explain
</user_query>

---

**Assistant**

Looking at the terminal output, I can see the ETL process ran but failed at the upload stage. Let me examine the relevant files to understand the issue.

The error is clear: **the `currency_type` column doesn't exist in the database schema**, but the uploader is trying to insert data into it. Let me check the key files.

The user wants me to analyze the terminal output from their ETL process. Let me examine what's happening:

1. The ETL ran with `python main.py 90` (90 days back)
2. It fetched 3 types of records:
   - Publicadas (published): 4512 records, 46 pages → 1011 target institutions
   - Adjudicadas (awarded): 16539 records, 166 pages → 6110 target institutions
   - Modificadas (modified): 11734 records, 118 pages → 4967 target institutions

3. It then processed and uploaded:
   - 1011 publicadas parsed successfully
   - Uploaded to Supabase successfully
   - 271 were medical (27%)
   - Then tried to upload adjudicadas (973 records) but FAILED

4. The error: `Could not find the 'currency_type' column of 'licitaciones_medicas' in the schema cache` with code PGRST204

This is a schema mismatch error - the code is trying to insert a column that doesn't exist in the database table.

Let me look at the relevant files to understand the issue better.

---

**Assistant**

Let me check the currency_type migration file that's in the git status but may not have been applied:

Now I see the issue clearly! Let me check the 003_add_currency_type.sql file since that's likely where the column was supposed to be added.

---

**Assistant**

Now I have a complete picture. Here's the analysis:

---

## Analysis Summary

### What Happened

The ETL process ran for 90 days of data and successfully:
- Fetched **4,512 published** tenders (1,011 from target institutions)
- Fetched **16,539 awarded** tenders (6,110 from target institutions)  
- Fetched **11,734 modified** tenders (4,967 from target institutions)
- Parsed and uploaded the first batch (1,011 published tenders) successfully
- **Failed when uploading the second batch (awarded tenders)**

### Root Cause

**Schema mismatch**: The uploader is trying to insert data into a `currency_type` column that doesn't exist in the database yet.

```
APIError: {'message': "Could not find the 'currency_type' column of 'licitaciones_medicas' in the schema cache", 'code': 'PGRST204'}
```

### Why It Failed on Second Batch But Not First

Looking at the `upsert_licitaciones()` function in `uploader.py:113-117`:

```python:113:117:uploader.py
filtered = {
    k: v for k, v in mapped.items()
    if v is not None or k == "es_medica"
}
```

The uploader filters out `None` values **except** for `es_medica`. Since adjudicated tenders likely have a `currency_type` value (from the API response), it wasn't filtered out and was sent to the database. Published tenders apparently don't have this field populated, so it was `None` and got filtered out — which is why the first batch succeeded.

### The Fix

You have a migration file ready: `supabase/migrations/003_add_currency_type.sql`

**You need to run this SQL in your Supabase database:**

```sql
-- Add currency_type column to licitaciones_medicas
ALTER TABLE licitaciones_medicas
  ADD COLUMN IF NOT EXISTS currency_type TEXT;

-- Backfill from raw_data JSONB
UPDATE licitaciones_medicas
SET currency_type = raw_data->>'currency_type'
WHERE currency_type IS NULL
  AND raw_data->>'currency_type' IS NOT NULL;

-- Set default for rows without currency info
UPDATE licitaciones_medicas
SET currency_type = 'CRC'
WHERE currency_type IS NULL;

-- Create index for filtering by currency
CREATE INDEX IF NOT EXISTS idx_licitaciones_currency
  ON licitaciones_medicas(currency_type);

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';
```

### Also Note: Syntax Warning

There's a minor issue in `classifier.py` with an invalid escape sequence on line 12:
```
SyntaxWarning: invalid escape sequence '\s'
```

This doesn't break the code (it's just a warning), but it should be fixed by using a raw string prefix (`r"..."`) for regex patterns.

---

**Next step**: Apply the migration in Supabase SQL Editor, then re-run the ETL.

Perfect! Now I have a complete picture. Let me analyze the situation:

1. The ETL fetched successfully:
   - 1011 "publicadas" (published) tenders
   - 973 "adjudicadas" (awarded) tenders
   - 392 "modificadas" (modified) tenders

2. It successfully uploaded the first batch (publicadas - 1011 records)

3. Then it tried to upload the "adjudicadas" and failed because:
   - The uploader is trying to insert `currency_type` column (line 73 in uploader.py)
   - But this column doesn't exist in the database yet
   - Migration `003_add_currency_type.sql` exists but hasn't been applied to the database

4. The error code PGRST204 means PostgREST (Supabase's REST API layer) couldn't find the column in its schema cache.

So the fix is simple: run the migration file `003_add_currency_type.sql` in Supabase to add the missing column.

---
