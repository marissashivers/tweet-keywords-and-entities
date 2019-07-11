# libraries
library(packcircles)
library(ggplot2)
library(viridis)

# Create data
#data=data.frame(group=paste("Group", letters[1:20]), value=sample(seq(1,100),20)) 
data=read.csv(file.choose(), fileEncoding="UTF-8-BOM")

# Generate the layout. sizetype can be area or radius, following your preference on what to be proportional to value.
packing <- circleProgressiveLayout(data$count, sizetype='area')
data = cbind(data, packing)
dat.gg <- circleLayoutVertices(packing, npoints=50)

# 2 -- Custom the color of the dots: proportional to the value:
# First I need to add the 'value' of each group to dat.gg.
# Here I repeat each value 51 times since I create my polygons with 50 lines
dat.gg$value=rep(data$sentiment, each=51)
g <- ggplot() + 
  
  # Make the bubbles
  geom_polygon(data = dat.gg, aes(x,y,group=id, fill=value), colour="black", alpha=0.6) + 
  scale_fill_distiller(palette = "RdYlGn", direction = 0 ) +
  
  # Add text in the center of each bubble + control its size
  geom_text(data = data, aes(x, y, size=2, label = text)) +
  scale_size_continuous(range = c(1,4)) +
  
  # General theme:
  theme_void()  + 
  theme(legend.position="none") + 
  coord_equal()

print(g)