# neuralHelicopter
Simple Helicopter game with a neural network AI evolved using a simple genetic algorith,

The game parameters can be edited using the main()
```
t = game(50, 20)
# Usage is game (#Generations, #Players)
```

There is always a human player. Once the generation is complete, the best model is saved in ./models/

The next generation takes the 2 best players, randomly takes weights from each and sometimes increases/decreases them slightly by a change factor.

25% of the time, a mutation happens and the weights randomly get multiplied by value from [-1, 1].

tkinter, keras and numpy are required to run this application

# Sample Run

![Alt text](img/heli.gif?raw=true "Sample Run")
