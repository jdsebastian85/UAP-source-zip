# Entity collapse report (T3)

Input: 11090 rows in entities.csv (untouched). Output: 11090 rows in entities_normalized.csv.

Rows changed: 806. Rule firings: {'RANK': 334, 'MARKING': 439, 'LAPAZ': 33}.

`value_normalized` is a retrieval convenience only. `value_verbatim` is the evidence and is preserved on every row.

## Merge decisions (every distinct rewrite, with row counts)

`Le.Paz`/`LePaz` are merged into `LaPaz` on the authority of CONTEXT_BRIEF.md, which documents them as known OCR splittings of the same name; this is not a fresh inference.

| n | type | verbatim | normalized |
|---|------|----------|------------|
| 115 | MARKING | `Declassified` | `DECLASSIFIED` |
| 109 | MARKING | `secret` | `SECRET` |
| 98 | MARKING | `Secret` | `SECRET` |
| 22 | MARKING | `confidential` | `CONFIDENTIAL` |
| 21 | PERSON | `Lt. Colonel` | `Lt Col` |
| 18 | PERSON | `Lt. Col` | `Lt Col` |
| 16 | MARKING | `restricted` | `RESTRICTED` |
| 15 | MARKING | `Top Secret` | `TOP SECRET` |
| 13 | MARKING | `Restricted` | `RESTRICTED` |
| 13 | MARKING | `declassified` | `DECLASSIFIED` |
| 12 | MARKING | `top secret` | `TOP SECRET` |
| 11 | PERSON | `Dr. La.Paz` | `Dr. LaPaz` |
| 9 | PERSON | `Lt Colonel` | `Lt Col` |
| 8 | PERSON | `Dr. Le.Paz` | `Dr. LaPaz` |
| 6 | MARKING | `Confidential` | `CONFIDENTIAL` |
| 6 | MARKING | `unclassified` | `UNCLASSIFIED` |
| 5 | PERSON | `Dr. LaPa.z` | `Dr. LaPaz` |
| 5 | MARKING | `NOfORN` | `NOFORN` |
| 5 | MARKING | `Unclassified` | `UNCLASSIFIED` |
| 4 | PERSON | `Capt. Tom Brown` | `Capt Tom Brown` |
| 4 | PERSON | `Col. Glenn` | `Col Glenn` |
| 4 | PERSON | `Lt. Col. Garrett` | `Lt Col Garrett` |
| 3 | PERSON | `Brig. Gen. Leo A. Geary` | `Brig Gen Leo A. Geary` |
| 3 | PERSON | `Col. Garrett` | `Col Garrett` |
| 3 | PERSON | `Col. McCoy` | `Col McCoy` |
| 3 | PERSON | `Dr. LePaz` | `Dr. LaPaz` |
| 3 | PERSON | `Lt. Col Garrett` | `Lt Col Garrett` |
| 3 | PERSON | `Lt. Gen. Donald L. Putt` | `Lt Gen Donald L. Putt` |
| 2 | PERSON | `Brig. Gen. Jack C. Ledford` | `Brig Gen Jack C. Ledford` |
| 2 | PERSON | `Capt. Hathaway` | `Capt Hathaway` |
| 2 | PERSON | `Capt. Stoney` | `Capt Stoney` |
| 2 | PERSON | `Col. Jack C. Ledford` | `Col Jack C. Ledford` |
| 2 | PERSON | `Col. O'Mara` | `Col O'Mara` |
| 2 | PERSON | `Col. William Shelton` | `Col William Shelton` |
| 2 | PERSON | `Dr. La Paz` | `Dr. LaPaz` |
| 2 | PERSON | `Dr. Lincoln La Paz` | `Dr. Lincoln LaPaz` |
| 2 | PERSON | `Gen. Andrew J. Goodpaster` | `Gen Andrew J. Goodpaster` |
| 2 | PERSON | `Gen. Curtis E. LeMay` | `Gen Curtis E. LeMay` |
| 2 | PERSON | `Gen. Doolittle` | `Gen Doolittle` |
| 2 | PERSON | `Lt. Col. Donald L. Springer` | `Lt Col Donald L. Springer` |
| 2 | PERSON | `Lt. Col. Ge.rrett` | `Lt Col Ge.rrett` |
| 2 | PERSON | `Lt. Col. USAF` | `Lt Col USAF` |
| 2 | PERSON | `Lt. Colonel Harold A. Steiner` | `Lt Col Harold A. Steiner` |
| 2 | PERSON | `Lt. Glen L. Stalker` | `Lt Glen L. Stalker` |
| 2 | PERSON | `Lt.Col. Garrett` | `Lt Col Garrett` |
| 2 | PERSON | `Maj. Gen. Patrick J. Halloran` | `Maj Gen Patrick J. Halloran` |
| 2 | PERSON | `Maj. John Seaberg` | `Maj John Seaberg` |
| 2 | PERSON | `Sgt. David Tellotson` | `Sgt David Tellotson` |
| 1 | PERSON | `Brig. Gen. Andrew J. Goodpaster` | `Brig Gen Andrew J. Goodpaster` |
| 1 | PERSON | `Brig. Gen. Bernard A. Schriever's Office` | `Brig Gen Bernard A. Schriever's Office` |
| 1 | PERSON | `Brig. Gen. Harold F. Knowles` | `Brig Gen Harold F. Knowles` |
| 1 | PERSON | `Brig. Gen. Howard G. Bunker Distribution` | `Brig Gen Howard G. Bunker Distribution` |
| 1 | PERSON | `Brig. Gen. Jack C. Ledford. USAF` | `Brig Gen Jack C. Ledford. USAF` |
| 1 | PERSON | `Brig. Gen. Maj. Gen. Lt. Gen` | `Brig Gen Maj. Gen. Lt. Gen` |
| 1 | PERSON | `Brig. Gen. Ralph E` | `Brig Gen Ralph E` |
| 1 | MARKING | `CONFIDENTIAl` | `CONFIDENTIAL` |
| 1 | PERSON | `Capt. A` | `Capt A` |
| 1 | PERSON | `Capt. AC Reser-` | `Capt AC Reser-` |
| 1 | PERSON | `Capt. Augusto Orrego` | `Capt Augusto Orrego` |
| 1 | PERSON | `Capt. Boshoff` | `Capt Boshoff` |
| 1 | PERSON | `Capt. C. S. Chiles` | `Capt C. S. Chiles` |
| 1 | PERSON | `Capt. Christiernsson` | `Capt Christiernsson` |
| 1 | PERSON | `Capt. Da-r` | `Capt Da-r` |
| 1 | PERSON | `Capt. Dant` | `Capt Dant` |
| 1 | PERSON | `Capt. E` | `Capt E` |
| 1 | PERSON | `Capt. E. J. Ruppelt` | `Capt E. J. Ruppelt` |
| 1 | PERSON | `Capt. Edgar` | `Capt Edgar` |
| 1 | PERSON | `Capt. Eldridge` | `Capt Eldridge` |
| 1 | PERSON | `Capt. Frank J. Morris` | `Capt Frank J. Morris` |
| 1 | PERSON | `Capt. Hathaway AACS` | `Capt Hathaway AACS` |
| 1 | PERSON | `Capt. Kenju Terauchi` | `Capt Kenju Terauchi` |
| 1 | PERSON | `Capt. Mantell. But` | `Capt Mantell. But` |
| 1 | PERSON | `Capt. Neil` | `Capt Neil` |
| 1 | PERSON | `Capt. Orrego` | `Capt Orrego` |
| 1 | PERSON | `Capt. Paul R. Stoney` | `Capt Paul R. Stoney` |
| 1 | PERSON | `Capt. Peter Killian` | `Capt Peter Killian` |
| 1 | PERSON | `Capt. Phil Schultz` | `Capt Phil Schultz` |
| 1 | PERSON | `Capt. Smi` | `Capt Smi` |
| 1 | PERSON | `Capt. Smith` | `Capt Smith` |
| 1 | PERSON | `Capt. Thomas` | `Capt Thomas` |
| 1 | PERSON | `Capt. Thomas F. Mantell` | `Capt Thomas F. Mantell` |
| 1 | PERSON | `Capt. Tom Bi` | `Capt Tom Bi` |
| 1 | PERSON | `Capt. Ulf Christiernsson` | `Capt Ulf Christiernsson` |
| 1 | PERSON | `Capt. V. I. Grissom` | `Capt V. I. Grissom` |
| 1 | PERSON | `Cdr. E. W. Hribar` | `Cmdr E. W. Hribar` |
| 1 | PERSON | `Cdr. Grierson` | `Cmdr Grierson` |
| 1 | PERSON | `Cdr. Schirra` | `Cmdr Schirra` |
| 1 | PERSON | `Cdr. William Holcomb` | `Cmdr William Holcomb` |
| 1 | PERSON | `Cmdr. Hammond Ceast Guard Hq` | `Cmdr Hammond Ceast Guard Hq` |
| 1 | PERSON | `Cmdr. Schirra` | `Cmdr Schirra` |
| 1 | PERSON | `Cmdr. Walter Schirra` | `Cmdr Walter Schirra` |
| 1 | PERSON | `Col. Adams` | `Col Adams` |
| 1 | PERSON | `Col. Adams's` | `Col Adams's` |
| 1 | PERSON | `Col. Al Outlon` | `Col Al Outlon` |
| 1 | PERSON | `Col. Allman T. Culbertson` | `Col Allman T. Culbertson` |
| 1 | PERSON | `Col. Andrew J. Goodpaster` | `Col Andrew J. Goodpaster` |
| 1 | PERSON | `Col. Bernard A. Schriever` | `Col Bernard A. Schriever` |
| 1 | PERSON | `Col. Donald D. Flickinger` | `Col Donald D. Flickinger` |
| 1 | PERSON | `Col. F` | `Col F` |
| 1 | PERSON | `Col. F. J. Clark` | `Col F. J. Clark` |
| 1 | PERSON | `Col. Frank O. Adams` | `Col Frank O. Adams` |
| 1 | PERSON | `Col. Frederick McCoy` | `Col Frederick McCoy` |
| 1 | PERSON | `Col. G. R. Dodson` | `Col G. R. Dodson` |
| 1 | PERSON | `Col. Ga` | `Col Ga` |
| 1 | PERSON | `Col. Ga.rl'ett` | `Col Ga.rl'ett` |
| 1 | PERSON | `Col. Garre` | `Col Garre` |
| 1 | PERSON | `Col. George Freeman` | `Col George Freeman` |
| 1 | PERSON | `Col. George Goddard. By` | `Col George Goddard. By` |
| 1 | PERSON | `Col. Glenn's` | `Col Glenn's` |
| 1 | PERSON | `Col. Harry Johnsto` | `Col Harry Johnsto` |
| 1 | PERSON | `Col. Ho` | `Col Ho` |
| 1 | PERSON | `Col. Hood` | `Col Hood` |
| 1 | PERSON | `Col. Hood's` | `Col Hood's` |
| 1 | PERSON | `Col. Jack A. Gibbs` | `Col Jack A. Gibbs` |
| 1 | PERSON | `Col. Jack A. Gibbs. Osmund` | `Col Jack A. Gibbs. Osmund` |
| 1 | PERSON | `Col. John Mccurdy` | `Col John Mccurdy` |
| 1 | PERSON | `Col. Kncmeyer` | `Col Kncmeyer` |
| 1 | PERSON | `Col. L. J. M. Mulhall` | `Col L. J. M. Mulhall` |
| 1 | PERSON | `Col. Leo Geary` | `Col Leo Geary` |
| 1 | PERSON | `Col. Leo P. Geary` | `Col Leo P. Geary` |
| 1 | PERSON | `Col. Ma.cDuff COMi` | `Col Ma.cDuff COMi` |
| 1 | PERSON | `Col. MacDuff` | `Col MacDuff` |
| 1 | PERSON | `Col. Marvin Stanley` | `Col Marvin Stanley` |
| 1 | PERSON | `Col. McCe` | `Col McCe` |
| 1 | PERSON | `Col. McCurdy Tribune` | `Col McCurdy Tribune` |
| 1 | PERSON | `Col. McOoJ` | `Col McOoJ` |
| 1 | PERSON | `Col. Milton F. Summerfelt` | `Col Milton F. Summerfelt` |
| 1 | PERSON | `Col. OWynne` | `Col OWynne` |
| 1 | PERSON | `Col. Olson` | `Col Olson` |
| 1 | PERSON | `Col. Osmond Ritla` | `Col Osmond Ritla` |
| 1 | PERSON | `Col. Osmund J. Rieland. He` | `Col Osmund J. Rieland. He` |
| 1 | PERSON | `Col. Osmund Ritland` | `Col Osmund Ritland` |
| 1 | PERSON | `Col. Philip J. Cono` | `Col Philip J. Cono` |
| 1 | PERSON | `Col. Richard S. Leghorn` | `Col Richard S. Leghorn` |
| 1 | PERSON | `Col. SPRINGER` | `Col SPRINGER` |
| 1 | PERSON | `Col. Stanley Beerli` | `Col Stanley Beerli` |
| 1 | PERSON | `Col. Stanley W. Beerli` | `Col Stanley W. Beerli` |
| 1 | PERSON | `Col. Steiners Encleaed` | `Col Steiners Encleaed` |
| 1 | PERSON | `Col. TAYLOR` | `Col TAYLOR` |
| 1 | PERSON | `Col. Tay SURNAME OF COORDINATING` | `Col Tay SURNAME OF COORDINATING` |
| 1 | PERSON | `Col. Taylor Lt. Col` | `Col Taylor Lt. Col` |
| 1 | PERSON | `Col. USAF` | `Col USAF` |
| 1 | PERSON | `Col. Vilhelm Evan` | `Col Vilhelm Evan` |
| 1 | PERSON | `Col. W. Randolph Lovelace` | `Col W. Randolph Lovelace` |
| 1 | PERSON | `Col. William Burke` | `Col William Burke` |
| 1 | PERSON | `Col. William Burke. Acting Chic` | `Col William Burke. Acting Chic` |
| 1 | PERSON | `Col. William Burke. Acting Chief` | `Col William Burke. Acting Chief` |
| 1 | PERSON | `Col. William F. Yancey` | `Col William F. Yancey` |
| 1 | MARKING | `DEClASSIFIED` | `DECLASSIFIED` |
| 1 | PERSON | `Dr. La.Paz. NW` | `Dr. LaPaz. NW` |
| 1 | PERSON | `Dr. Lincoln La.Paz For Sandia` | `Dr. Lincoln LaPaz For Sandia` |
| 1 | PERSON | `Gen. Ayub Khan` | `Gen Ayub Khan` |
| 1 | PERSON | `Gen. Bengt Norderskjold` | `Gen Bengt Norderskjold` |
| 1 | PERSON | `Gen. Bunker` | `Gen Bunker` |
| 1 | PERSON | `Gen. C. Mi` | `Gen C. Mi` |
| 1 | PERSON | `Gen. Cari Spaatz` | `Gen Cari Spaatz` |
| 1 | PERSON | `Gen. Carroll` | `Gen Carroll` |
| 1 | PERSON | `Gen. Charles Pearre Cabell` | `Gen Charles Pearre Cabell` |
| 1 | PERSON | `Gen. Chiang Ching-kuo` | `Gen Chiang Ching-kuo` |
| 1 | PERSON | `Gen. Curt` | `Gen Curt` |
| 1 | PERSON | `Gen. Denis Letty` | `Gen Denis Letty` |
| 1 | PERSON | `Gen. Doolittle's` | `Gen Doolittle's` |
| 1 | PERSON | `Gen. George C. Kenney` | `Gen George C. Kenney` |
| 1 | PERSON | `Gen. Inv` | `Gen Inv` |
| 1 | PERSON | `Gen. James` | `Gen James` |
| 1 | PERSON | `Gen. James Doolittle` | `Gen James Doolittle` |
| 1 | PERSON | `Gen. James H. Doolittle` | `Gen James H. Doolittle` |
| 1 | PERSON | `Gen. Ll'Bailly` | `Gen Ll'Bailly` |
| 1 | PERSON | `Gen. Marshall S. Carter` | `Gen Marshall S. Carter` |
| 1 | PERSON | `Gen. Maxwell Taylor` | `Gen Maxwell Taylor` |
| 1 | PERSON | `Gen. Nathan` | `Gen Nathan` |
| 1 | PERSON | `Gen. Patrick Hurlev` | `Gen Patrick Hurlev` |
| 1 | PERSON | `Gen. Samford` | `Gen Samford` |
| 1 | PERSON | `Gen. Smith` | `Gen Smith` |
| 1 | PERSON | `Gen. Sory Smith. Air` | `Gen Sory Smith. Air` |
| 1 | PERSON | `Gen. Thomas T` | `Gen Thomas T` |
| 1 | PERSON | `Gen. Werner` | `Gen Werner` |
| 1 | PERSON | `Lt Colonel Georie Garrett` | `Lt Col Georie Garrett` |
| 1 | PERSON | `Lt Colonel Hippler` | `Lt Col Hippler` |
| 1 | PERSON | `Lt Colonel Pvrior` | `Lt Col Pvrior` |
| 1 | PERSON | `Lt Colonel Steiner` | `Lt Col Steiner` |
| 1 | PERSON | `Lt Colonel Steiner AFBSA` | `Lt Col Steiner AFBSA` |
| 1 | PERSON | `Lt Gen. Twin` | `Lt Gen Twin` |
| 1 | PERSON | `Lt. Brigham` | `Lt Brigham` |
| 1 | PERSON | `Lt. Carl W. Stucld` | `Lt Carl W. Stucld` |
| 1 | PERSON | `Lt. Cdr` | `Lt Cdr` |
| 1 | PERSON | `Lt. Cdr. Carpenter` | `Lt Cdr. Carpenter` |
| 1 | PERSON | `Lt. Cdr. Carpenter's` | `Lt Cdr. Carpenter's` |
| 1 | PERSON | `Lt. Cdr. US Navy-` | `Lt Cdr. US Navy-` |
| 1 | PERSON | `Lt. Cmdr. Walter Schirra` | `Lt Cmdr. Walter Schirra` |
| 1 | PERSON | `Lt. Co` | `Lt Co` |
| 1 | PERSON | `Lt. Col Oarret.t` | `Lt Col Oarret.t` |
| 1 | PERSON | `Lt. Col. DONALD L. SPRINGER` | `Lt Col DONALD L. SPRINGER` |
| 1 | PERSON | `Lt. Col. Farrior` | `Lt Col Farrior` |
| 1 | PERSON | `Lt. Col. Ga.rrett` | `Lt Col Ga.rrett` |
| 1 | PERSON | `Lt. Col. Garre` | `Lt Col Garre` |
| 1 | PERSON | `Lt. Col. Gee` | `Lt Col Gee` |
| 1 | PERSON | `Lt. Col. Gerrett` | `Lt Col Gerrett` |
| 1 | PERSON | `Lt. Col. Harold A. Steiner` | `Lt Col Harold A. Steiner` |
| 1 | PERSON | `Lt. Col. Harold A. Steiner Aasiatar` | `Lt Col Harold A. Steiner Aasiatar` |
| 1 | PERSON | `Lt. Col. JOHN O'MARA. The` | `Lt Col JOHN O'MARA. The` |
| 1 | PERSON | `Lt. Col. John H. Glenn` | `Lt Col John H. Glenn` |
| 1 | PERSON | `Lt. Col. John R. Hood` | `Lt Col John R. Hood` |
| 1 | PERSON | `Lt. Col. Joseph J. Pellegrini` | `Lt Col Joseph J. Pellegrini` |
| 1 | PERSON | `Lt. Col. Leo P. Geary` | `Lt Col Leo P. Geary` |
| 1 | PERSON | `Lt. Col. O'Mara` | `Lt Col O'Mara` |
| 1 | PERSON | `Lt. Col. O'Mara's` | `Lt Col O'Mara's` |
| 1 | PERSON | `Lt. Col. OONALD L. SPRmGER` | `Lt Col OONALD L. SPRmGER` |
| 1 | PERSON | `Lt. Col. Richard Leghorn` | `Lt Col Richard Leghorn` |
| 1 | PERSON | `Lt. Col. Robert E. Hervey` | `Lt Col Robert E. Hervey` |
| 1 | PERSON | `Lt. Col. STANLEY JACOBS` | `Lt Col STANLEY JACOBS` |
| 1 | PERSON | `Lt. Col. USAF' J.S` | `Lt Col USAF' J.S` |
| 1 | PERSON | `Lt. Col. USAP Jot` | `Lt Col USAP Jot` |
| 1 | PERSON | `Lt. Col. V. T. Ford` | `Lt Col V. T. Ford` |
| 1 | PERSON | `Lt. Col.. DONALD L. SPRINGER` | `Lt Col.. DONALD L. SPRINGER` |
| 1 | PERSON | `Lt. Col.. Jobn R` | `Lt Col.. Jobn R` |
| 1 | PERSON | `Lt. Col.. SmiW` | `Lt Col.. SmiW` |
| 1 | PERSON | `Lt. Collina` | `Lt Collina` |
| 1 | PERSON | `Lt. Colliu` | `Lt Colliu` |
| 1 | PERSON | `Lt. Colo` | `Lt Colo` |
| 1 | PERSON | `Lt. Colone` | `Lt Colone` |
| 1 | PERSON | `Lt. Colonel DONALD L. SPRE` | `Lt Col DONALD L. SPRE` |
| 1 | PERSON | `Lt. Colonel DONALD SPRINGER` | `Lt Col DONALD SPRINGER` |
| 1 | PERSON | `Lt. Colonel. U.S.A.P. File` | `Lt Col U.S.A.P. File` |
| 1 | PERSON | `Lt. Combs` | `Lt Combs` |
| 1 | PERSON | `Lt. Comdr. Marcus L. Lowe` | `Lt Comdr. Marcus L. Lowe` |
| 1 | PERSON | `Lt. Commander Lowe` | `Lt Commander Lowe` |
| 1 | PERSON | `Lt. Commander MELVIN MICHAEL KUHN` | `Lt Commander MELVIN MICHAEL KUHN` |
| 1 | PERSON | `Lt. DAVIS` | `Lt DAVIS` |
| 1 | PERSON | `Lt. David C. Brigham` | `Lt David C. Brigham` |
| 1 | PERSON | `Lt. Gen` | `Lt Gen` |
| 1 | PERSON | `Lt. Gen. Charles Pearre Cabell` | `Lt Gen Charles Pearre Cabell` |
| 1 | PERSON | `Lt. Gen. D. L. Putt` | `Lt Gen D. L. Putt` |
| 1 | PERSON | `Lt. Gen. L` | `Lt Gen L` |
| 1 | PERSON | `Lt. Gen. Mairshall S. Carter` | `Lt Gen Mairshall S. Carter` |
| 1 | PERSON | `Lt. General Schaper` | `Lt Gen Schaper` |
| 1 | PERSON | `Lt. George F. C-orman` | `Lt George F. C-orman` |
| 1 | PERSON | `Lt. George F. Gorman` | `Lt George F. Gorman` |
| 1 | PERSON | `Lt. Gov. Whitehead` | `Lt Gov. Whitehead` |
| 1 | PERSON | `Lt. Halllllakar` | `Lt Halllllakar` |
| 1 | PERSON | `Lt. Hamaker` | `Lt Hamaker` |
| 1 | PERSON | `Lt. Henry G. Combs` | `Lt Henry G. Combs` |
| 1 | PERSON | `Lt. KUHN` | `Lt KUHN` |
| 1 | PERSON | `Lt. Kenwood W. Jackson` | `Lt Kenwood W. Jackson` |
| 1 | PERSON | `Lt. LOUIS SAUTER` | `Lt LOUIS SAUTER` |
| 1 | PERSON | `Lt. Mantell` | `Lt Mantell` |
| 1 | PERSON | `Lt. Offl'l` | `Lt Offl'l` |
| 1 | PERSON | `Lt. Robert` | `Lt Robert` |
| 1 | PERSON | `Lt. Robert White` | `Lt Robert White` |
| 1 | PERSON | `Lt. Ryan` | `Lt Ryan` |
| 1 | PERSON | `Lt. Rym` | `Lt Rym` |
| 1 | PERSON | `Lt. SAUTER` | `Lt SAUTER` |
| 1 | PERSON | `Lt. SriJ.t.h` | `Lt SriJ.t.h` |
| 1 | PERSON | `Lt. Ueyars` | `Lt Ueyars` |
| 1 | PERSON | `Lt.Col Robart B. Hughes` | `Lt Col Robart B. Hughes` |
| 1 | PERSON | `LtCol Ste` | `Lt Col Ste` |
| 1 | PERSON | `Maj. A. B` | `Maj A. B` |
| 1 | PERSON | `Maj. Alexander` | `Maj Alexander` |
| 1 | PERSON | `Maj. D. D. Pomerleau` | `Maj D. D. Pomerleau` |
| 1 | PERSON | `Maj. Donald E. Kcyhoe` | `Maj Donald E. Kcyhoe` |
| 1 | PERSON | `Maj. Gen. Curtis E. LeMay` | `Maj Gen Curtis E. LeMay` |
| 1 | PERSON | `Maj. Gen. Gordon P. Saville` | `Maj Gen Gordon P. Saville` |
| 1 | PERSON | `Maj. Gen. H. McK. Roper` | `Maj Gen H. McK. Roper` |
| 1 | PERSON | `Maj. Gen. John A. Sa` | `Maj Gen John A. Sa` |
| 1 | PERSON | `Maj. Joseph P. Martino` | `Maj Joseph P. Martino` |
| 1 | PERSON | `Maj. Lt. Col. Col` | `Maj Lt. Col. Col` |
| 1 | PERSON | `Maj. Phipps` | `Maj Phipps` |
| 1 | PERSON | `Maj. Pomerleau` | `Maj Pomerleau` |
| 1 | PERSON | `Maj. Rudolph Anderson` | `Maj Rudolph Anderson` |
| 1 | PERSON | `Maj. USAF JS Original` | `Maj USAF JS Original` |
| 1 | PERSON | `Maj. Walter L. Cara` | `Maj Walter L. Cara` |
| 1 | PERSON | `Maj. William Metscher` | `Maj William Metscher` |
| 1 | MARKING | `NoFORN` | `NOFORN` |
| 1 | MARKING | `RESTRiCTED` | `RESTRICTED` |
| 1 | PERSON | `Sgt. CHARLES M. HOWARD` | `Sgt CHARLES M. HOWARD` |
| 1 | PERSON | `Sgt. GORDON RICH ARDSON` | `Sgt GORDON RICH ARDSON` |
| 1 | PERSON | `Sgt. Kinaley'o` | `Sgt Kinaley'o` |

## Candidates NOT merged (judgment calls, left as-is)

These resemble known names but differ by letters, not just dots, spacing, or case. Merging them would be an inference, so they stand verbatim in both columns:

- `Dr. La.Pa` (x1) — resembles LaPaz but letters differ/truncated
- `Dr. LaPa` (x1) — resembles LaPaz but letters differ/truncated
- `Dr. LaPar` (x1) — resembles LaPaz but letters differ/truncated
- `Lt Col Garret` (x2) — resembles Garrett but letters differ
- `Lt. Col. Ge.rrett` (x2) — resembles Garrett but letters differ
- `Lt. Col. Gerrett` (x1) — resembles Garrett but letters differ

## DocId truncation check

Rows matching a DocId pattern in entities.csv: 0. The truncated DocId stamps noted in the earlier 48-item snapshot are not present in this extraction, so no DocId collapse was performed.
