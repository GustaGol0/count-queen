# Count & Queen — direção de arte

O acabamento combina fantasia ilustrada, caricatura moderada, verde profundo,
vinho, papel marfim e latão envelhecido. A orientação final é manter personagens
adultos e expressivos, sem exagerar nas proporções. Animações movimentam os
retratos inteiros; os rostos não possuem animação facial independente.

## Arte integrada

- Arquivo no jogo: `count_queen/web_ui/portraits-atlas.png`.
- Ferramenta: geração e edição de imagens integrada (ImageGen); sem CLI alternativa.
- Um atlas com nove quadros iguais, recortados pela interface sem alterar o PNG.
- Ordem: Ferrugem, Frei, Íris; Véspera, Cobrador, Duquesa; Astrônomo, Rei, jogadora da estrada.
- Os elites reutilizam retratos temáticos. As duas Gêmeas têm quadros próprios.
- Origem: edição de um primeiro atlas pintado, gerado para este projeto. A escolha
  final priorizou o resultado visual após o pedido de moderar a caricatura.

## Prompt final de edição utilizado

O prompt foi enviado antes da orientação final de moderar a caricatura. O texto
abaixo é o registro real da geração, e não uma nova especificação de proporções.

```text
EDIT TARGET: the supplied 3 by 3 portrait atlas for Count & Queen. Preserve EXACT 3x3 equal square tile grid, character ordering, outfits' identity colors, props and the very dark forest green background. Dramatically change the artistic style from realistic oil portraits to highly appealing CARICATURED 2D fantasy game character illustrations. Make them unmistakably drawn cartoon characters with oversized heads (head takes about 60% of each portrait), small narrow shoulders, wildly expressive exaggerated brows and eyes, bold distinctive noses and jaw shapes, large simplified hair shapes, angular ink outlines and clean graphic cel-shaded painterly color blocks. Expressive, slightly mischievous and theatrical medieval card-game mood, sophisticated comic-book storybook art suitable for a stylish indie game, not babyish chibi. Remove ALL photorealistic skin, pores, lifelike anatomy, realistic material rendering, intricate tiny texture. Matte flat colors and two or three tone dramatic lighting, broad brush accents, crisp silhouettes. Every character must have a distinctly different silhouette and exaggerated expression. TOP LEFT: Madame Ferrugem, big auburn bun, enormous arched eyebrow, sly crooked grin, elongated sharp nose, brass earrings, burgundy coat, holding coin. TOP CENTER: Frei Sete-Sinos, huge frowning brow, long angular nose, thin pinched mouth, oversized ivory hood, seven simple bells across chest. TOP RIGHT: Iris, very pointy chin, huge swept silver hair, angular violet eye mask and cloak, devious wide smirk, mirror. MIDDLE LEFT: Vespera, same adult twin identity but rounder hair silhouette sweeping opposite direction, teal mask and cloak, heavy skeptical eyelids, unimpressed pout, mirror. MIDDLE CENTER: Cobrador, ridiculously long thin face and nose, tiny round glasses, tall exaggerated top hat, pursed lips, red ledger. MIDDLE RIGHT: Duquesa, enormous sculptural charcoal hair, dramatic cheekbones, haughty raised chin, black dress and tiny glowing brazier. BOTTOM LEFT: Astronomo, huge fluffy curled beard, oversized star-pattern blindfold, long curved nose, indigo robe, big brass astrolabe. BOTTOM CENTER: Rei, oversized angular gold crown, enormous triangular burgundy collar, tiny black featureless face opening, broad theatrical silhouette, antique gold medallion. BOTTOM RIGHT: tavern gambler, big asymmetrical short black hair, strong square jaw, one raised eyebrow, lopsided smile, green jacket, fan of cards. Keep all subjects adult. Exactly nine tiles, one person entirely contained per tile. No text, no numbers, no divider lines or margins, no watermarks. Make the transformation strongly caricatured, not merely smoothed realistic faces.
```
