// JavaScript pour changer la couleur de fond des carrés
function changeSquareColor() {
    var squares = document.querySelectorAll('.square');

    squares.forEach(function(square) {
        // Génération d'une couleur hexadécimale aléatoire
        var randomColor = '#' + Math.floor(Math.random()*16777215).toString(16);

        // Changement de la couleur de fond du carré
        square.style.backgroundColor = randomColor;
    });
}

// Appel de la fonction au chargement de la page (vous pouvez appeler la fonction selon votre logique)
window.onload = changeSquareColor;
