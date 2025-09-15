
def _calculate_position_corrected(self, h_align: str, v_align: str, x_offset: int, y_offset: int,
                                margin_h: int, margin_v: int, video_size: Tuple[int, int]) -> Union[str, Tuple]:
    """
    CORRECTED position calculation that accounts for MoviePy text positioning behavior.
    
    MoviePy positions text clips by their CENTER point, not top-left corner.
    This method calculates the correct center position for the text.
    """
    width, height = video_size
    
    # For MoviePy, we can use string-based positioning which is more reliable
    # than pixel coordinates for text alignment
    
    if h_align == 'center' and v_align == 'bottom':
        # Use MoviePy's built-in positioning with offset
        if y_offset != 0:
            # Calculate bottom position with offset
            bottom_y = height + y_offset - margin_v
            return ('center', bottom_y)
        else:
            # Use built-in bottom positioning with margin
            return ('center', height - margin_v)
    
    elif h_align == 'center' and v_align == 'middle':
        center_y = height // 2 + y_offset
        return ('center', center_y)
    
    elif h_align == 'center' and v_align == 'top':
        top_y = margin_v + y_offset
        return ('center', top_y)
    
    else:
        # For other alignments, calculate pixel positions
        if h_align == 'left':
            x_pos = margin_h + x_offset
        elif h_align == 'right':
            x_pos = width - margin_h + x_offset
        else:  # center
            x_pos = width // 2 + x_offset
        
        if v_align == 'top':
            y_pos = margin_v + y_offset
        elif v_align == 'bottom':
            # Account for text height by using a safe margin
            y_pos = height - margin_v + y_offset
        else:  # middle
            y_pos = height // 2 + y_offset
        
        return (x_pos, y_pos)
