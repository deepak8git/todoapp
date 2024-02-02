from kivymd.app import MDApp
from kivy.lang.builder import Builder
#from kivy.core.window import Window
import uuid
from kivymd.uix.list import OneLineAvatarIconListItem,IconLeftWidget,IconRightWidget
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.label import Label
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.uix.boxlayout import BoxLayout
import sqlite3
#Window.size=(400,700)

conn=sqlite3.connect("todo.db")
command= "create table if not exists todo (id text, task text)"
conn.execute(command)
conn.commit()


KV="""
MDBoxLayout:    
    orientation:"vertical"
    #md_bg_color: app.theme_cls.primary_light
    
    MDBoxLayout:
        padding:10
        spacing:10
        pos_hint:{"y":0.9}
        size_hint_y:0.1
        #md_bg_color: app.theme_cls.primary_dark    

        MDTextField:
            id:inputtodo
            hint_text:"insert you text here"
            mode:"fill"
            required:True
            size_hint_x:0.6
        
        MDRaisedButton:
            text:"Add"
            #md_bg_color:"orange"
            on_release:app.addnewrecord(inputtodo.text)
            
    MDBoxLayout:
        #md_bg_color:app.theme_cls.primary_light
        MDScrollView:
            MDList:
                id:todolist
<Content>    
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "60dp"

    MDTextField:
        id:edittext1
        hint_text: "edit data"
"""

class Content(BoxLayout):
    pass

class ToDoListApp(MDApp):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.all_record=[]
        self.mydialog=None

    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.screen = Builder.load_string(KV)        
        return self.screen
    
    def on_start(self):
        
        self.loadrecord()
    
    def loadrecord(self):
        #print("task started")
        cursor=conn.execute('SELECT * FROM todo ORDER BY id DESC')
        task=cursor.fetchall()
        
        #print(task)
        todolist=self.screen.ids.todolist        
        for row in task:   
            self.all_record.append(
                {"value":row[1],"id":row[0]}
            )

        for x in self.all_record:   

            ids=x['id']
            values=x['value']

            print(type(ids))

            todolist.add_widget(
                OneLineAvatarIconListItem(
                    IconLeftWidget(
                        icon="pencil",
                        on_release=lambda x,item_id=ids: self.editbtn(item_id)
                    ),
                    IconRightWidget(
                        icon="delete",
                        on_release=lambda x,item_id=ids:self.deletebtn(item_id)
                    ),

                    on_press=lambda x, item_id=ids: self.on_task_press(item_id),
                    id=ids,
                    text=values
                ) 
            ) 
        
        #print(self.all_record)             

    def on_task_press(self, item_id):
        pass

    def addnewrecord(self,record):
       
        if record:
            item_id=str(uuid.uuid4())
            self.all_record.append(
                {"value":record,"id":item_id}
            )

            print(type(item_id))

            todolist=self.screen.ids.todolist
            
            todolist.add_widget(
                OneLineAvatarIconListItem(
                    IconLeftWidget(
                        icon="pencil",
                        on_release=lambda x:self.editbtn(item_id)
                    ),
                    IconRightWidget(
                        icon="delete",
                        on_release=lambda x:self.deletebtn(item_id)
                    ),
                    id=item_id,
                    text=record
                ) 
            )
           
            conn.execute("insert into todo (id,task) values(?,?)",(item_id,record))
            conn.commit()

        self.screen.ids.inputtodo.text=""

    def editbtn(self,dataid):
        if not self.mydialog:
            self.dialog=MDDialog(
                title="Update Data",
                type="custom",  
                content_cls=Content(),

                buttons=[
                    MDFlatButton(
                        text="save",
                        text_color="red",
                        on_release=lambda x:self.saverecord(dataid,self.dialog.content_cls.ids.edittext1.text)                        
                    )
                ]
            )
               
        self.dialog.open()
        #self.dialog.content_cls.ids.edittext1.text=dataid
      


    def saverecord(self,dataid,value):

        
        self.dialog.dismiss()

        for x in self.all_record:
            if x["id"]==dataid:
                x["value"]=value

        todolist=self.screen.ids.todolist
        for child in todolist.children:
            if child.id==dataid:
                child.text=value
        conn.execute('UPDATE todo SET task = ?  WHERE id = ?', (value, dataid))
        conn.commit()
        print(dataid)


    def deletebtn(self,dataid):
        
        for x in self.all_record:
            if x["id"]==dataid:
                self.all_record.remove(x)

        todolist=self.screen.ids.todolist
        for child in todolist.children:
            if child.id==dataid:
                todolist.remove_widget(child)

        conn.execute('DELETE FROM todo WHERE id = ?', (dataid,))
        conn.commit()

if __name__ == "__main__":
    ToDoListApp().run()
