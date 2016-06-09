from django.contrib import admin
from django import forms
from gazetteer.models import Location,LocationName
from skosxl.models import Notation
from .settings import TARGET_NAMESPACE_FT

# Register your models here.

# works for Dango > 1.6 
class NameInline(admin.TabularInline):
    model = LocationName

    
class LocationTypeInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LocationTypeInlineForm, self).__init__(*args, **kwargs)
        self.fields['locationType'].queryset = Notation.objects.filter(concept__scheme__uri = TARGET_NAMESPACE_FT[0:-1] )

class LocationTypeInline(admin.StackedInline) :
    model = Notation
    form = LocationTypeInlineForm
        
class LocationAdmin(admin.ModelAdmin):
    inlines = [
        NameInline,
    ]

        
#admin.site.register(LocationType);
admin.site.register(Location, LocationAdmin);
admin.site.register(LocationName);