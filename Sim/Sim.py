from direct.showbase.ShowBase import ShowBase
 
class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)

        self.environ = self.loader.loadModel("models/environment")
        self.environ.reparentTo(self.render)
        self.environ.setScale(.25,.25,.25)
        self.environ.setPos(-8,42,0)
 
app = MyApp()
app.run()
