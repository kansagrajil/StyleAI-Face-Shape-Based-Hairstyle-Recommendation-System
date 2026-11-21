/**
 * Face Shape Helper Utilities — Provides real face shape SVG illustrations, 
 * descriptions, and badge generators for all 7 supported face shapes.
 */

const FaceShapeHelper = (() => {
    const SHAPES = {
        oval: {
            name: 'Oval',
            icon: '/assets/images/faceshapes/oval.svg',
            color: '#818cf8',
            desc: 'Balanced length to width ratio, soft rounded jawline.'
        },
        round: {
            name: 'Round',
            icon: '/assets/images/faceshapes/round.svg',
            color: '#f472b6',
            desc: 'Equal length and width with soft curved contours.'
        },
        square: {
            name: 'Square',
            icon: '/assets/images/faceshapes/square.svg',
            color: '#38bdf8',
            desc: 'Strong angular jawline and proportional forehead width.'
        },
        heart: {
            name: 'Heart',
            icon: '/assets/images/faceshapes/heart.svg',
            color: '#e879f9',
            desc: 'Wider forehead tapering gracefully to a pointed chin.'
        },
        oblong: {
            name: 'Oblong',
            icon: '/assets/images/faceshapes/oblong.svg',
            color: '#34d399',
            desc: 'Elongated face length with straight cheek lines.'
        },
        diamond: {
            name: 'Diamond',
            icon: '/assets/images/faceshapes/diamond.svg',
            color: '#fbbf24',
            desc: 'Dramatic cheekbones with narrower forehead and chin.'
        },
        triangle: {
            name: 'Triangle',
            icon: '/assets/images/faceshapes/triangle.svg',
            color: '#2dd4bf',
            desc: 'Wider jawline base tapering up to a narrow forehead.'
        }
    };

    function getShapeData(shapeKey) {
        const key = (shapeKey || '').toLowerCase().trim();
        return SHAPES[key] || {
            name: shapeKey || 'Oval',
            icon: '/assets/images/faceshapes/oval.svg',
            color: '#818cf8',
            desc: 'Unique facial structure and geometry.'
        };
    }

    function getIconUrl(shapeKey) {
        return getShapeData(shapeKey).icon;
    }

    function getImgTag(shapeKey, size = 48, extraClass = '') {
        const data = getShapeData(shapeKey);
        return `<img src="${data.icon}" alt="${data.name} Face Shape" width="${size}" height="${size}" class="face-shape-img ${extraClass}" title="${data.name} Face Shape">`;
    }

    function getBadgeHtml(shapeKey, showLabel = true) {
        const data = getShapeData(shapeKey);
        return `
            <span class="d-inline-flex align-items-center gap-2 px-3 py-1.5 rounded-pill bg-dark border border-white-10 text-light shadow-sm">
                <img src="${data.icon}" width="24" height="24" alt="${data.name}">
                ${showLabel ? `<strong class="text-capitalize" style="color: ${data.color}">${data.name}</strong>` : ''}
            </span>
        `;
    }

    return {
        SHAPES,
        getShapeData,
        getIconUrl,
        getImgTag,
        getBadgeHtml
    };
})();

if (typeof window !== 'undefined') {
    window.FaceShapeHelper = FaceShapeHelper;
}
