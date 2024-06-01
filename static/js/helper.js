difficultyStylingDict = {
    '1' : 'aqua',
    '2' : 'green',
    '3' : 'yellow',
    '4' : 'orange',
    '5' : 'red',
    '6' : 'purple',
    '7-9' : 'darkgrey'
}


function changeHighlights(difficultyLevel) {
    relevantSpanTags = document.querySelectorAll(`[data-category="${difficultyLevel}"]`);
    
    // Check if they are highlighted or not
    if (relevantSpanTags.length == 0) {
        return;
    }

    relevantClass = difficultyStylingDict[difficultyLevel];

    relevantSpanTags.forEach(function(spanTag) {
        // Turn class on or off
        if (spanTag.classList.contains(relevantClass)) {
            spanTag.classList.remove(relevantClass);
        } else {
            spanTag.classList.add(relevantClass)
        }
        
    });
}