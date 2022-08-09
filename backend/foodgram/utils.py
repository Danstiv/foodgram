import os


def prettify_recipe_image(recipe, update=False):
    dirname, filename = os.path.split(recipe.image.path)
    filename, extension = os.path.splitext(filename)
    new_filename = f'{recipe.id}{extension}'
    new_path = os.path.join(dirname, new_filename)
    if update:
        os.remove(new_path)
    os.rename(recipe.image.path, new_path)
    dirname, filename = os.path.split(recipe.image.name)
    recipe.image.name = os.path.join(dirname, new_filename)
    recipe.save()
    return recipe
