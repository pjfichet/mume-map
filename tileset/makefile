# Uncomment your desired player tile
PLAYER=helf-light
#PLAYER=cleric
#PLAYER=warrior
#PLAYER=orc
#PLAYER=troll

TILESDIR=../mumemap/tiles


TILES=field field-dark brush brush-dark forest forest-dark \
hill hill-dark mountain mountain-dark swamp swamp-dark \
water water-dark rapid rapid-dark underwater underwater-dark \
cavern cavern-dark tunnel tunnel-dark road road-dark city city-dark \
indoor indoor-dark random random-dark undefined \
armour label exitdown exitup guild \
herb key quest rent shop aggressive-mob super-mob elite-mob treasure \
walleast wallnorth wallsouth wallwest weapon elf elf-dark elf-light \
elf-grey cleric warrior orc troll helf-light helf-dark \
root noid path attention helmet


all: $(TILESDIR) $(TILES:%=$(TILESDIR)/%.png) $(TILESDIR)/player.png

$(TILESDIR):
	mkdir -p $@

$(TILESDIR)/%.png: %-multi.png
	mv $< $@

$(TILESDIR)/player.png: $(TILESDIR)/$(PLAYER).png
	cd $(TILESDIR) && ln -s $(PLAYER).png player.png

%-multi.png: %
	xcf2png tiles-multi.xcf $< > $@

%-mono.png: %
	xcf2png tiles-mono.xcf $< > $@

%-green.png: %-mono.png
	convert $< -fill '#204631' -opaque '#1A2B2F'\
		-fill '#527F39' -opaque '#273F45'\
		-fill '#AEC440' -opaque '#4D767E'\
		-fill '#D7E894' -opaque '#7CC5D2' $@

%-gold.png: %-mono.png
	convert $< -fill '#2F0E09' -opaque '#1A2B2F'\
		-fill '#4B2C0D' -opaque '#273F45'\
		-fill '#826418' -opaque '#4D767E'\
		-fill '#DCC32C' -opaque '#7CC5D2' $@

clean:
	@rm -f $(TILES:%=%.png)
	@rm -f player.png

.PHONY: $(TILES) $(TERRAIN)

