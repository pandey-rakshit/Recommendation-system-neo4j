/******************************************************
 *  MOVIE CARD TEMPLATE (No overlay poster, no duplicate)
 ******************************************************/
function movieCard(movie) {
    const posterUrl = movie.poster_url || "";

    return `
    <div class="movie-card hover-card" data-poster="${posterUrl}">
        
        <!-- Poster -->
        <div class="poster-wrapper">
            <img class="poster" style="display:none;">
            <div class="no-poster" style="display:none;">No Image</div>
        </div>

        <!-- Always visible title -->
        <div class="card-title">${movie.title || "Untitled"}</div>

        <!-- Expanding info panel on hover -->
        <div class="hover-info">
            <h3>${movie.title || "Untitled"}</h3>

            <p class="overview">
                ${movie.overview ? movie.overview.substring(0, 80) + "..." : "No overview available."}
            </p>

            <span class="meta">
                ⭐ ${movie.vote_average || "N/A"} |
                🎬 ${movie.release_year || "----"} |
                👍 ${movie.vote_count || 0}
            </span>
        </div>
    </div>`;
}


/******************************************************
 *  POSTER VALIDATION (404-proof)
 ******************************************************/
function verifyPosters() {
    document.querySelectorAll(".movie-card").forEach(card => {
        const posterUrl = card.dataset.poster;
        const img = new Image();

        const posterElem = card.querySelector(".poster");
        const noPosterElem = card.querySelector(".no-poster");

        if (!posterUrl) {
            noPosterElem.style.display = "flex";
            return;
        }

        img.onload = () => {
            posterElem.src = posterUrl;
            posterElem.style.display = "block";
        };

        img.onerror = () => {
            noPosterElem.style.display = "flex";
        };

        img.src = posterUrl;
    });
}


/******************************************************
 *  RENDER HOMEPAGE SECTIONS
 ******************************************************/
function renderHomeSections(sections) {
    document.getElementById("popular").innerHTML =
        (sections.popular || []).map(movieCard).join("");

    document.getElementById("trending").innerHTML =
        (sections.trending || []).map(movieCard).join("");

    document.getElementById("topRated").innerHTML =
        (sections.topRated || []).map(movieCard).join("");

    verifyPosters();
}


/******************************************************
 *  LOAD HOMEPAGE SECTIONS (with caching)
 ******************************************************/
async function loadHomeSections() {
    const cacheKey = "homepage_sections_cache";

    const cached = sessionStorage.getItem(cacheKey);
    if (cached) {
        renderHomeSections(JSON.parse(cached));
        return;
    }

    const res = await fetch(`/api/catalog?sections=`);
    const data = await res.json();

    sessionStorage.setItem(cacheKey, JSON.stringify(data.sections));

    renderHomeSections(data.sections);
}


/******************************************************
 *  RENDER SEARCH RESULTS
 ******************************************************/
function renderSearchResults(data) {
    document.getElementById("search-results").innerHTML =
        data.search_results.map(movieCard).join("");

    document.getElementById("recommendations").innerHTML =
        data.recommendations.map(movieCard).join("");

    verifyPosters();
}


/******************************************************
 *  LOAD SEARCH RESULTS (with caching)
 ******************************************************/
async function loadSearchResults(query) {
    const cacheKey = "search_" + query.toLowerCase();

    const cached = sessionStorage.getItem(cacheKey);
    if (cached) {
        renderSearchResults(JSON.parse(cached));
        return;
    }

    const res = await fetch(`/api/catalog/search?q=${query}`);
    const data = await res.json();

    sessionStorage.setItem(cacheKey, JSON.stringify(data));

    renderSearchResults(data);
}


/******************************************************
 *  DYNAMIC SECTIONS (Infinite scroll)
 ******************************************************/
const dynamicSections = [
    "action",
    "comedy",
    "drama"
];

let nextSectionIndex = 0;
let loadingMoreSections = false;

async function loadNextSection() {
    if (loadingMoreSections) return;
    if (nextSectionIndex >= dynamicSections.length) return;

    loadingMoreSections = true;

    const section = dynamicSections[nextSectionIndex];
    nextSectionIndex++;

    const sectionId = `section_${section}`;

    // add new section block
    const html = `
        <h2 class="section-title">${section.toUpperCase()}</h2>
        <div id="${sectionId}" class="movie-grid"></div>
    `;
    document.getElementById("home-mode").insertAdjacentHTML("beforeend", html);

    // caching
    const cacheKey = "section_cache_" + section;
    const cached = sessionStorage.getItem(cacheKey);

    if (cached) {
        const movies = JSON.parse(cached);
        document.getElementById(sectionId).innerHTML =
            movies.map(movieCard).join("");
        verifyPosters();
        loadingMoreSections = false;
        return;
    }

    // fetch
    const res = await fetch(`/api/catalog?sections=${section}`);
    const data = await res.json();
    const movies = data.sections[section] || [];

    sessionStorage.setItem(cacheKey, JSON.stringify(movies));

    document.getElementById(sectionId).innerHTML =
        movies.map(movieCard).join("");

    verifyPosters();
    loadingMoreSections = false;
}


/******************************************************
 *  PAGE INIT
 ******************************************************/
async function init() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get("q");

    if (!query) {
        document.getElementById("home-mode").style.display = "block";
        document.getElementById("search-mode").style.display = "none";
        await loadHomeSections();
    } else {
        document.getElementById("home-mode").style.display = "none";
        document.getElementById("search-mode").style.display = "block";
        await loadSearchResults(query);
    }
}

init();


/******************************************************
 *  INFINITE SCROLL LISTENER
 ******************************************************/
window.addEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 300) {
        loadNextSection();
    }
});
