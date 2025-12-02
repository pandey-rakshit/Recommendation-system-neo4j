/******************************************************
 *  CONFIGURATION
 ******************************************************/
const PLACEHOLDER_IMAGE = "/static/imgs/no_img.png";


/******************************************************
 *  MOVIE CARD TEMPLATE
 ******************************************************/
function movieCard(movie) {
    const posterUrl = movie.poster_url || PLACEHOLDER_IMAGE;

    return `
    <div class="movie-card hover-card" data-poster="${posterUrl}">
        
        <!-- Poster -->
        <div class="poster-wrapper">
            <img class="poster" style="display:none;">
            <img class="placeholder" src="${PLACEHOLDER_IMAGE}" style="display:none;">
        </div>

        <!-- Movie Title -->
        <div class="card-title">${movie.title || "Untitled"}</div>

        <!-- Hover Panel -->
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
 *  POSTER VALIDATION (404-SAFE)
 ******************************************************/
function verifyPosters() {
    document.querySelectorAll(".movie-card").forEach(card => {
        const posterUrl = card.dataset.poster;
        const img = new Image();

        const posterElem = card.querySelector(".poster");
        const placeholderElem = card.querySelector(".placeholder");

        if (!posterUrl || posterUrl.trim() === "") {
            placeholderElem.style.display = "block";
            return;
        }

        img.onload = () => {
            posterElem.src = posterUrl;
            posterElem.style.display = "block";
        };

        img.onerror = () => {
            placeholderElem.style.display = "block";
        };

        img.src = posterUrl;
    });
}


/******************************************************
 *  HOMEPAGE LOADING (DYNAMIC + CONDITIONAL)
 ******************************************************/
function renderHomeSections(sections) {
    const container = document.getElementById("dynamic-sections");
    container.innerHTML = ""; // reset

    Object.keys(sections).forEach(name => {
        const movies = sections[name];
        if (!movies || movies.length < 4) return; // skip small sections

        const sectionHtml = `
            <div class="section-block">
                <h2 class="section-title">${name}</h2>
                <div id="section-${name}" class="movie-grid">
                    ${movies.map(movieCard).join("")}
                </div>
            </div>
        `;

        container.insertAdjacentHTML("beforeend", sectionHtml);
    });

    verifyPosters();
}


/******************************************************
 *  LOAD HOMEPAGE SECTIONS (DYNAMIC)
 ******************************************************/
async function loadHomeSections() {
    const container = document.getElementById("dynamic-sections");
    const loading = document.getElementById("loading-placeholder");

    try {
        const res = await fetch(`/api/catalog?sections=`);
        const data = await res.json();

        // hide loading skeleton
        loading.style.display = "none";

        // render dynamic sections
        renderHomeSections(data.sections);

        // cache it
        sessionStorage.setItem("homepage_sections_cache", JSON.stringify(data.sections));

    } catch (err) {
        console.error("Error loading homepage sections", err);
        loading.innerHTML = "<p>Error loading content.</p>";
    }
}


/******************************************************
 *  SEARCH RESULTS
 ******************************************************/
function renderSearchResults(data) {
    const searchContainer = document.getElementById("search-results-container");
    const recContainer = document.getElementById("recommendations-container");

    // hide container if empty
    if (!data.search_results.length) {
        searchContainer.style.display = "none";
    } else {
        searchContainer.style.display = "block";
        document.getElementById("search-results").innerHTML =
            data.search_results.map(movieCard).join("");
    }

    if (!data.recommendations.length) {
        recContainer.style.display = "none";
    } else {
        recContainer.style.display = "block";
        document.getElementById("recommendations").innerHTML =
            data.recommendations.map(movieCard).join("");
    }

    verifyPosters();
}


/******************************************************
 *  LOAD SEARCH RESULTS (with caching)
 ******************************************************/
async function loadSearchResults(query) {
    const cacheKey = "search_" + query.toLowerCase();

    if (sessionStorage.getItem(cacheKey)) {
        renderSearchResults(JSON.parse(sessionStorage.getItem(cacheKey)));
        return;
    }

    const res = await fetch(`/api/catalog/search?q=${query}`);
    const data = await res.json();

    sessionStorage.setItem(cacheKey, JSON.stringify(data));

    renderSearchResults(data);
}


/******************************************************
 *  DYNAMIC LAZY-SECTIONS (Action, Comedy, Drama…)
 ******************************************************/
const dynamicSections = ["action", "comedy", "drama"];
let nextSectionIndex = 0;
let loadingMore = false;

async function loadNextSection() {
    if (loadingMore) return;
    if (nextSectionIndex >= dynamicSections.length) return;

    loadingMore = true;

    const section = dynamicSections[nextSectionIndex++];
    const container = document.getElementById("dynamic-sections");

    const sectionHtml = `
        <div class="section-block">
            <h2 class="section-title">${section}</h2>
            <div id="dynamic-${section}" class="movie-grid"></div>
        </div>
    `;
    container.insertAdjacentHTML("beforeend", sectionHtml);

    const cacheKey = "section_cache_" + section;

    if (sessionStorage.getItem(cacheKey)) {
        const movies = JSON.parse(sessionStorage.getItem(cacheKey));
        document.getElementById(`dynamic-${section}`).innerHTML =
            movies.map(movieCard).join("");
        verifyPosters();
        loadingMore = false;
        return;
    }

    const res = await fetch(`/api/catalog?sections=${section}`);
    const data = await res.json();
    const movies = data.sections[section] || [];

    sessionStorage.setItem(cacheKey, JSON.stringify(movies));

    document.getElementById(`dynamic-${section}`).innerHTML =
        movies.map(movieCard).join("");

    verifyPosters();
    loadingMore = false;
}


/******************************************************
 *  INIT PAGE
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
 *  INFINITE SCROLL TRIGGER
 ******************************************************/
window.addEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 200) {
        loadNextSection();
    }
});
